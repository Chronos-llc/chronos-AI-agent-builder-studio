from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SupportStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class SupportPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SupportCategory(str, Enum):
    BUG = "BUG"
    FEATURE_REQUEST = "FEATURE_REQUEST"
    BILLING = "BILLING"
    TECHNICAL = "TECHNICAL"
    ACCOUNT = "ACCOUNT"
    OTHER = "OTHER"


class SupportMessageBase(BaseModel):
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    priority: SupportPriority = SupportPriority.NORMAL
    category: Optional[SupportCategory] = None


class SupportMessageCreate(SupportMessageBase):
    pass


class SupportMessageUpdate(BaseModel):
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1)
    status: Optional[SupportStatus] = None
    priority: Optional[SupportPriority] = None
    assigned_to: Optional[int] = None
    category: Optional[SupportCategory] = None


class SupportMessageResponse(SupportMessageBase):
    id: int
    user_id: int
    status: SupportStatus
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SupportMessageList(BaseModel):
    items: List[SupportMessageResponse]
    total: int
    page: int
    page_size: int


class SupportMessageReplyBase(BaseModel):
    reply_text: str = Field(..., min_length=1)


class SupportMessageReplyCreate(SupportMessageReplyBase):
    pass


class SupportMessageReplyResponse(SupportMessageReplyBase):
    id: int
    message_id: int
    user_id: int
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SupportMessageReplyList(BaseModel):
    items: List[SupportMessageReplyResponse]
    total: int
    page: int
    page_size: int


class SupportSearchParams(BaseModel):
    query: Optional[str] = None
    status: Optional[SupportStatus] = None
    priority: Optional[SupportPriority] = None
    category: Optional[SupportCategory] = None
    assigned_to: Optional[int] = None
    sort_by: Optional[str] = "created_at"  # created_at, updated_at, priority
    sort_order: Optional[str] = "desc"  # asc, desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)