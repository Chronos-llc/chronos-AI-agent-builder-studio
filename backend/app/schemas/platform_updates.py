from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UpdateType(str, Enum):
    FEATURE = "FEATURE"
    BUG_FIX = "BUG_FIX"
    ANNOUNCEMENT = "ANNOUNCEMENT"
    MAINTENANCE = "MAINTENANCE"
    SECURITY = "SECURITY"


class UpdatePriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TargetAudience(str, Enum):
    ALL = "ALL"
    ADMIN = "ADMIN"
    USER = "USER"


class PlatformUpdateBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    update_type: UpdateType = UpdateType.ANNOUNCEMENT
    priority: UpdatePriority = UpdatePriority.NORMAL
    media_type: Optional[str] = Field(None, max_length=20)  # IMAGE, VIDEO, NONE
    media_urls: Optional[List[str]] = None
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    target_audience: TargetAudience = TargetAudience.ALL


class PlatformUpdateCreate(PlatformUpdateBase):
    pass


class PlatformUpdateUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    update_type: Optional[UpdateType] = None
    priority: Optional[UpdatePriority] = None
    media_type: Optional[str] = Field(None, max_length=20)
    media_urls: Optional[List[str]] = None
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    target_audience: Optional[TargetAudience] = None
    is_published: Optional[bool] = None
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class PlatformUpdateResponse(PlatformUpdateBase):
    id: int
    is_published: bool
    view_count: int
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PlatformUpdateList(BaseModel):
    items: List[PlatformUpdateResponse]
    total: int
    page: int
    page_size: int


class UserUpdateViewResponse(BaseModel):
    id: int
    update_id: int
    user_id: int
    viewed_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdateViewList(BaseModel):
    items: List[UserUpdateViewResponse]
    total: int
    page: int
    page_size: int