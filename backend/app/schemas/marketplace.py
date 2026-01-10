"""
Marketplace Pydantic Schemas

Defines request and response schemas for marketplace API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ListingType(str, Enum):
    AGENT = "AGENT"
    SUBAGENT = "SUBAGENT"


class Visibility(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    UNLISTED = "UNLISTED"


class ModerationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# Marketplace Category Schemas
class MarketplaceCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    sort_order: int = 0


class MarketplaceCategoryCreate(MarketplaceCategoryBase):
    pass


class MarketplaceCategoryUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class MarketplaceCategoryResponse(MarketplaceCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MarketplaceCategoryList(BaseModel):
    items: List[MarketplaceCategoryResponse]
    total: int
    page: int
    page_size: int


# Marketplace Tag Schemas
class MarketplaceTagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class MarketplaceTagCreate(MarketplaceTagBase):
    pass


class MarketplaceTagUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MarketplaceTagResponse(MarketplaceTagBase):
    id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MarketplaceTagList(BaseModel):
    items: List[MarketplaceTagResponse]
    total: int
    page: int
    page_size: int

# Marketplace Listing Schemas
class MarketplaceListingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    listing_type: ListingType = ListingType.AGENT
    visibility: Visibility = Visibility.PUBLIC
    version: Optional[str] = None
    preview_images: Optional[List[str]] = None
    demo_video_url: Optional[str] = None


class MarketplaceListingCreate(MarketplaceListingBase):
    agent_id: int
    schema_data: Optional[Dict[str, Any]] = None


class MarketplaceListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    visibility: Optional[Visibility] = None
    version: Optional[str] = None
    preview_images: Optional[List[str]] = None
    demo_video_url: Optional[str] = None
    schema_data: Optional[Dict[str, Any]] = None


class MarketplaceListingResponse(MarketplaceListingBase):
    id: int
    agent_id: int
    author_id: int
    moderation_status: ModerationStatus
    moderation_notes: Optional[str] = None
    schema_data: Optional[Dict[str, Any]] = None
    install_count: int
    rating_average: float
    rating_count: int
    view_count: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MarketplaceListingList(BaseModel):
    items: List[MarketplaceListingResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# Marketplace Installation Schemas
class MarketplaceInstallationCreate(BaseModel):
    listing_id: int


class MarketplaceInstallationResponse(BaseModel):
    id: int
    listing_id: int
    user_id: int
    agent_id: int
    installed_at: datetime
    
    class Config:
        from_attributes = True


# Marketplace Review Schemas
class MarketplaceReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None


class MarketplaceReviewCreate(MarketplaceReviewBase):
    listing_id: int


class MarketplaceReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = None


class MarketplaceReviewResponse(MarketplaceReviewBase):
    id: int
    listing_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MarketplaceReviewList(BaseModel):
    items: List[MarketplaceReviewResponse]
    total: int
    page: int
    page_size: int


# Moderation Schemas
class ModerationAction(BaseModel):
    moderation_status: ModerationStatus
    moderation_notes: Optional[str] = None


# Search and Filter Schemas
class MarketplaceSearchParams(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    listing_type: Optional[ListingType] = None
    sort_by: Optional[str] = "created_at"  # created_at, rating, installs, views
    sort_order: Optional[str] = "desc"  # asc, desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
