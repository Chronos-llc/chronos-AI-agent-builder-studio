from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import desc, func

from app.models.integration import Integration as IntegrationModel
from app.models.user import User as UserModel
from app.schemas.integration import (
    IntegrationCreate, IntegrationUpdate, IntegrationResponse,
    IntegrationConfigCreate, IntegrationConfigUpdate, IntegrationConfigResponse,
    IntegrationReviewCreate, IntegrationReviewResponse,
    IntegrationMarketplaceSearch, IntegrationUsageStats
)
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.integration import IntegrationConfig as IntegrationConfigModel
from app.models.integration import IntegrationReview as IntegrationReviewModel


router = APIRouter()


@router.post("/integrations/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new integration for the marketplace"""
    db_integration = IntegrationModel(
        **integration.dict(),
        author_id=current_user.id
    )
    db.add(db_integration)
    await db.commit()
    await db.refresh(db_integration)
    return db_integration


@router.get("/integrations/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """Get integration details"""
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    integration = result.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.put("/integrations/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    integration: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update an integration"""
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    db_integration = result.scalars().first()
    if not db_integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Check if user is the author
    if db_integration.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this integration")
    
    for key, value in integration.dict(exclude_unset=True).items():
        setattr(db_integration, key, value)
    
    await db.commit()
    await db.refresh(db_integration)
    return db_integration


@router.delete("/integrations/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Delete an integration"""
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    db_integration = result.scalars().first()
    if not db_integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Check if user is the author
    if db_integration.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this integration")
    
    await db.delete(db_integration)
    await db.commit()


@router.post("/integrations/search/", response_model=List[IntegrationResponse])
async def search_integrations(
    search_params: IntegrationMarketplaceSearch,
    db: Session = Depends(get_db)
):
    """Search integrations in the marketplace"""
    query = select(IntegrationModel)
    
    # Filter by query
    if search_params.query:
        query = query.where(
            IntegrationModel.name.ilike(f"%{search_params.query}%") |
            IntegrationModel.description.ilike(f"%{search_params.query}%")
        )
    
    # Filter by categories
    if search_params.categories:
        query = query.where(IntegrationModel.category.in_(search_params.categories))
    
    # Filter by types
    if search_params.types:
        query = query.where(IntegrationModel.integration_type.in_(search_params.types))
    
    # Filter by minimum rating
    if search_params.min_rating:
        query = query.where(IntegrationModel.rating >= search_params.min_rating)
    
    # Sort
    if search_params.sort_by == "popularity":
        query = query.order_by(desc(IntegrationModel.download_count))
    elif search_params.sort_by == "rating":
        query = query.order_by(desc(IntegrationModel.rating))
    elif search_params.sort_by == "newest":
        query = query.order_by(desc(IntegrationModel.created_at))
    else:
        query = query.order_by(desc(IntegrationModel.download_count))
    
    # Pagination
    offset = (search_params.page - 1) * search_params.page_size
    query = query.offset(offset).limit(search_params.page_size)
    
    result = await db.execute(query)
    integrations = result.scalars().all()
    return integrations


@router.post("/integrations/{integration_id}/config/", response_model=IntegrationConfigResponse)
async def create_integration_config(
    integration_id: int,
    config: IntegrationConfigCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create configuration for an integration"""
    # Check if integration exists
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    integration = result.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    db_config = IntegrationConfigModel(
        integration_id=integration_id,
        user_id=current_user.id,
        **config.dict()
    )
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config


@router.get("/integrations/config/{config_id}", response_model=IntegrationConfigResponse)
async def get_integration_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get integration configuration"""
    result = await db.execute(
        select(IntegrationConfigModel).where(
            IntegrationConfigModel.id == config_id,
            IntegrationConfigModel.user_id == current_user.id
        )
    )
    config = result.scalars().first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/integrations/config/{config_id}", response_model=IntegrationConfigResponse)
async def update_integration_config(
    config_id: int,
    config: IntegrationConfigUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update integration configuration"""
    result = await db.execute(
        select(IntegrationConfigModel).where(
            IntegrationConfigModel.id == config_id,
            IntegrationConfigModel.user_id == current_user.id
        )
    )
    db_config = result.scalars().first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    for key, value in config.dict(exclude_unset=True).items():
        setattr(db_config, key, value)
    
    await db.commit()
    await db.refresh(db_config)
    return db_config


@router.post("/integrations/{integration_id}/reviews/", response_model=IntegrationReviewResponse)
async def create_integration_review(
    integration_id: int,
    review: IntegrationReviewCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a review for an integration"""
    # Check if integration exists
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    integration = result.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Check if user already reviewed
    result = await db.execute(
        select(IntegrationReviewModel).where(
            IntegrationReviewModel.integration_id == integration_id,
            IntegrationReviewModel.user_id == current_user.id
        )
    )
    existing_review = result.scalars().first()
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
    
    # Update integration rating
    result = await db.execute(
        select(func.avg(IntegrationReviewModel.rating)).where(
            IntegrationReviewModel.integration_id == integration_id
        )
    )
    avg_rating = result.scalar() or 0
    
    integration.rating = avg_rating
    integration.review_count = await db.execute(
        select(func.count()).where(
            IntegrationReviewModel.integration_id == integration_id
        )
    )
    integration.review_count = integration.review_count.scalar()
    
    await db.commit()
    return db_review


@router.get("/integrations/{integration_id}/stats/", response_model=IntegrationUsageStats)
async def get_integration_stats(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """Get usage statistics for an integration"""
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    integration = result.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # This would be enhanced with actual usage tracking in a real implementation
    return IntegrationUsageStats(
        integration_id=integration_id,
        usage_count=integration.download_count,
        success_count=integration.download_count * 0.9,  # Mock data
        error_count=integration.download_count * 0.1,   # Mock data
        avg_response_time=150.5  # Mock data in ms
    )