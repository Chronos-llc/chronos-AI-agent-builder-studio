"""
Skills Database Models

Defines the database models for skills and skill installations.
Skills are pre-built capabilities stored as files that admins can create and users can add to their agents.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class Skill(BaseModel):
    """Skill model for pre-built agent capabilities"""
    __tablename__ = "agent_skills"
    
    # Basic information
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True, index=True)
    icon = Column(String(50), nullable=True)
    
    # File Information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    content_preview = Column(Text, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, server_default='true', nullable=False, index=True)
    is_premium = Column(Boolean, server_default='false', nullable=False)
    install_count = Column(Integer, server_default='0', nullable=False)
    
    # Version and parameters
    version = Column(String(20), nullable=True)
    parameters = Column(JSON, nullable=True)  # Configurable parameters for the skill
    tags = Column(JSON, nullable=True)  # Tags for filtering and search
    
    # Admin Management
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    installations = relationship("AgentSkillInstallation", back_populates="skill", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.name}', category='{self.category}')>"


class AgentSkillInstallation(BaseModel):
    """Agent skill installation tracking"""
    __tablename__ = "agent_skill_installations"
    
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("agent_skills.id", ondelete="CASCADE"), nullable=False, index=True)
    knowledge_file_id = Column(Integer, ForeignKey("knowledge_files.id", ondelete="SET NULL"), nullable=True)
    
    # Configuration for this installation
    configuration = Column(JSON, nullable=True)  # User-specific configuration for the skill
    is_enabled = Column(Boolean, server_default='true', nullable=False)
    
    installed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    agent = relationship("AgentModel", foreign_keys=[agent_id])
    skill = relationship("Skill", back_populates="installations")
    knowledge_file = relationship("KnowledgeFile", foreign_keys=[knowledge_file_id])
    
    def __repr__(self):
        return f"<AgentSkillInstallation(id={self.id}, agent_id={self.agent_id}, skill_id={self.skill_id})>"
