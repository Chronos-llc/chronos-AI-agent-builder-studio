from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import ENUM
import enum

from app.models.base import BaseModel


class AgentStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class AgentModel(BaseModel):
    __tablename__ = "agents"
    
    # Basic information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(AgentStatus), default=AgentStatus.DRAFT, nullable=False)
    
    # Configuration
    model_config = Column(JSON, nullable=True)  # LLM configuration
    system_prompt = Column(Text, nullable=True)
    user_prompt_template = Column(Text, nullable=True)
    
    # Sub-agent configurations
    sub_agent_config = Column(JSON, nullable=True)  # Sub-agent specific configurations
    
    # Metadata
    tags = Column(JSON, nullable=True)  # List of tags
    metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # Percentage
    avg_response_time = Column(Float, default=0.0)  # Seconds
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="agents")
    versions = relationship("AgentVersion", back_populates="agent", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="agent", cascade="all, delete-orphan")
    hooks = relationship("Hook", back_populates="agent", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="agent", cascade="all, delete-orphan")
    integration_configs = relationship("IntegrationConfig", back_populates="agent", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="agent", cascade="all, delete-orphan")
    knowledge_files = relationship("KnowledgeFile", back_populates="agent", cascade="all, delete-orphan")
    knowledge_searches = relationship("KnowledgeSearch", back_populates="agent", cascade="all, delete-orphan")
    communication_channels = relationship("CommunicationChannel", back_populates="agent", cascade="all, delete-orphan")
    training_sessions = relationship("TrainingSession", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AgentModel(id={self.id}, name='{self.name}', status='{self.status}')>"


class AgentVersion(BaseModel):
    __tablename__ = "agent_versions"
    
    # Version information
    version_number = Column(String(20), nullable=False)
    changelog = Column(Text, nullable=True)
    is_current = Column(Boolean, default=False)
    
    # Configuration snapshot
    config_snapshot = Column(JSON, nullable=False)  # Complete agent config at this version
    
    # Foreign keys
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="versions")
    
    def __repr__(self):
        return f"<AgentVersion(id={self.id}, version='{self.version_number}', agent_id={self.agent_id})>"


class Action(BaseModel):
    __tablename__ = "actions"
    
    # Action information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    action_type = Column(String(50), nullable=False)  # function, api_call, web_scraping, etc.
    status = Column(String(20), default="draft", nullable=False)
    
    # Configuration
    parameters = Column(JSON, nullable=True)  # Action parameters
    config = Column(JSON, nullable=True)  # Action-specific configuration
    code = Column(Text, nullable=True)  # Custom code for the action
    input_schema = Column(JSON, nullable=True)  # Input schema validation
    output_schema = Column(JSON, nullable=True)  # Output schema validation
    dependencies = Column(JSON, nullable=True)  # List of dependencies
    timeout = Column(Integer, default=30)  # Timeout in seconds
    retry_policy = Column(JSON, nullable=True)  # Retry policy configuration
    
    # Foreign keys
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="actions")
    
    def __repr__(self):
        return f"<Action(id={self.id}, name='{self.name}', type='{self.action_type}')>"