from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
     
    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
     
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
     
    # Security
    login_attempts = Column(Integer, default=0)
    locked_until = Column(String(20), nullable=True)  # ISO datetime string

    # Retention and deletion lifecycle
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deletion_requested_at = Column(DateTime(timezone=True), nullable=True)
    purge_after = Column(DateTime(timezone=True), nullable=True)
     
    # Preferences
    theme = Column(String(20), default="light")  # light, dark, system
    language = Column(String(10), default="en")
     
    # Relationships
    agents = relationship("AgentModel", back_populates="owner", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")
    plan = relationship("UserPlan", back_populates="user", uselist=False, cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    integrations = relationship(
        "Integration",
        back_populates="author",
        cascade="all, delete-orphan",
        foreign_keys="Integration.author_id",
    )
    integration_configs = relationship("IntegrationConfig", back_populates="user", cascade="all, delete-orphan")
    integration_reviews = relationship("IntegrationReview", back_populates="user", cascade="all, delete-orphan")
    knowledge_searches = relationship("KnowledgeSearch", back_populates="user", cascade="all, delete-orphan")
    training_sessions = relationship("TrainingSession", back_populates="user", cascade="all, delete-orphan")
    personal_access_tokens = relationship("PersonalAccessToken", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
