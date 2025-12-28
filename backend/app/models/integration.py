from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Integration(BaseModel):
    __tablename__ = "integrations"
    
    # Integration information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    integration_type = Column(String(50), nullable=False)  # api, webhook, database, etc.
    
    # Configuration
    config = Column(JSON, nullable=False)  # Integration configuration
    credentials = Column(JSON, nullable=True)  # Encrypted credentials
    is_active = Column(Boolean, default=True)
    
    # Status
    last_sync = Column(String(20), nullable=True)  # ISO datetime
    sync_status = Column(String(20), default="never")  # never, success, error
    
    # Foreign keys
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)  # Optional - can be global
    
    # Relationships
    agent = relationship("AgentModel", back_populates="integrations")
    
    def __repr__(self):
        return f"<Integration(id={self.id}, name='{self.name}', type='{self.integration_type}')>"