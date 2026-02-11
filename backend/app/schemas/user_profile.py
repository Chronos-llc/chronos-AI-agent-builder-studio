from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class UserPersona(str):
    DEVELOPER = "developer"
    POWER_USER = "power_user"
    ENTERPRISE = "enterprise"


class UserProfileBase(BaseModel):
    persona: Optional[str] = Field(default=None, pattern="^(developer|power_user|enterprise)$")
    github_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    role_title: Optional[str] = Field(default=None, max_length=255)
    company_name: Optional[str] = Field(default=None, max_length=255)
    industry: Optional[str] = Field(default=None, max_length=120)
    team_size: Optional[str] = Field(default=None, max_length=80)
    use_cases: Optional[List[str]] = None
    tools_stack: Optional[List[str]] = None
    primary_goal: Optional[str] = Field(default=None, max_length=500)


class UserProfileUpdate(UserProfileBase):
    onboarding_completed: Optional[bool] = None


class UserOnboardingRequest(UserProfileBase):
    persona: str = Field(..., pattern="^(developer|power_user|enterprise)$")
    primary_goal: str = Field(..., min_length=3, max_length=500)


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

