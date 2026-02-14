from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class UserPersona(str, enum.Enum):
    DEVELOPER = "developer"
    POWER_USER = "power_user"
    ENTERPRISE = "enterprise"


class FuzzyOnboardingState(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    persona = Column(SQLEnum(UserPersona), nullable=True)

    github_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    role_title = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    industry = Column(String(120), nullable=True)
    team_size = Column(String(80), nullable=True)
    primary_goal = Column(String(500), nullable=True)

    use_cases = Column(JSON, nullable=True)
    tools_stack = Column(JSON, nullable=True)

    onboarding_completed = Column(Boolean, default=False, nullable=False)
    fuzzy_onboarding_state = Column(String(20), nullable=False, default=FuzzyOnboardingState.PENDING.value)
    fuzzy_onboarding_completed_at = Column(DateTime(timezone=True), nullable=True)
    fuzzy_onboarding_skipped_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="profile")
