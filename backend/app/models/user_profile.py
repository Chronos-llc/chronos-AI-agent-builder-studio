from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class UserPersona(str, enum.Enum):
    DEVELOPER = "developer"
    POWER_USER = "power_user"
    ENTERPRISE = "enterprise"


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

    user = relationship("User", back_populates="profile")

