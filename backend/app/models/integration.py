from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class Integration(BaseModel):
    __tablename__ = "integrations"
     
    # Integration information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    integration_type = Column(String(50), nullable=False)  # api, webhook, database, etc.
    category = Column(String(50), nullable=False)
    icon = Column(String(200), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    version = Column(String(20), default="1.0.0")
    is_public = Column(Boolean, default=True)
     
    # Configuration schemas
    config_schema = Column(JSON, nullable=False, default={})
    credentials_schema = Column(JSON, nullable=True)
    supported_features = Column(JSON, nullable=False, default=[])
     
    # Status and metrics
    last_sync = Column(String(20), nullable=True)  # ISO datetime
    sync_status = Column(String(20), default="never")  # never, success, error
    download_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
     
    # Foreign keys
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)  # Optional - can be global
     
    # Relationships
    author = relationship("User", back_populates="integrations")
    agent = relationship("AgentModel", back_populates="integrations")
    configs = relationship("IntegrationConfig", back_populates="integration", cascade="all, delete-orphan")
    reviews = relationship("IntegrationReview", back_populates="integration", cascade="all, delete-orphan")
     
    def __repr__(self):
        return f"<Integration(id={self.id}, name='{self.name}', type='{self.integration_type}')>"


class IntegrationConfig(BaseModel):
    __tablename__ = "integration_configs"
    
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    config = Column(JSON, nullable=False)
    credentials = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Foreign keys for agent-specific configs
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    # Relationships
    integration = relationship("Integration", back_populates="configs")
    user = relationship("User", back_populates="integration_configs")
    agent = relationship("AgentModel", back_populates="integration_configs")
    
    def __repr__(self):
        return f"<IntegrationConfig(id={self.id}, integration_id={self.integration_id}, user_id={self.user_id})>"


class IntegrationReview(BaseModel):
    __tablename__ = "integration_reviews"
    
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    
    # Relationships
    integration = relationship("Integration", back_populates="reviews")
    user = relationship("User", back_populates="integration_reviews")
    
    def __repr__(self):
        return f"<IntegrationReview(id={self.id}, integration_id={self.integration_id}, rating={self.rating})>"