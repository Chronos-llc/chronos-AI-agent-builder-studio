from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WorkspaceMemberCreate(BaseModel):
    member_user_id: int = Field(..., ge=1)
    role: str = Field(default="member", min_length=2, max_length=50)


class WorkspaceMemberResponse(BaseModel):
    id: int
    owner_user_id: int
    member_user_id: int
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

