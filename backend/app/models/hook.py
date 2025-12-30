from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Hook(BaseModel):
    __tablename__ = "hooks"
    
    # Hook information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    hook_type = Column(String(50), nullable=False)  # pre_process, post_process, error, etc.
    trigger = Column(String(50), nullable=False)  # before_action, after_action, on_error, etc.
    status = Column(String(20), default="active", nullable=False)
    
    # Configuration
    trigger_conditions = Column(JSON, nullable=True)  # Conditions that trigger this hook
    action_config = Column(JSON, nullable=False)  # What this hook does
    priority = Column(Integer, default=0)  # Execution priority
    is_global = Column(Boolean, default=False)  # Whether this hook is global
    dependencies = Column(JSON, nullable=True)  # List of dependencies
    timeout = Column(Integer, default=10)  # Timeout in seconds
    
    # Foreign keys
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)  # Optional - can be global
    
    # Relationships
    agent = relationship("AgentModel", back_populates="hooks")
    
    def __repr__(self):
        return f"<Hook(id={self.id}, name='{self.name}', type='{self.hook_type}')>"