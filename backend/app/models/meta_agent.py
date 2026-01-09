"""
Meta-Agent FUZZY Database Models

Defines the database tables for meta-agent configuration, command tracking,
and session management.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.types import JSON, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class PermissionLevel(enum.Enum):
    """Permission levels for meta-agent actions"""
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class CommandStatus(enum.Enum):
    """Status of meta-agent command execution"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionStatus(enum.Enum):
    """Status of meta-agent session"""
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMEOUT = "timeout"


class MetaAgent(BaseModel):
    """
    Main meta-agent configuration table.
    
    Stores the configuration and permissions for meta-agents that can
    orchestrate and execute multiple sub-agents and actions.
    """
    __tablename__ = "meta_agents"
    
    # Basic information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Permission configuration
    permission_level = Column(
        Enum(PermissionLevel), 
        default=PermissionLevel.EDITOR, 
        nullable=False
    )
    allowed_actions = Column(JSON, nullable=True)  # Array of allowed action types
    
    # Configuration
    configuration = Column(JSON, nullable=True)  # Meta-agent specific configuration
    
    # Relationships
    commands = relationship(
        "MetaAgentCommand", 
        back_populates="meta_agent", 
        cascade="all, delete-orphan"
    )
    sessions = relationship(
        "MetaAgentSession", 
        back_populates="meta_agent", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<MetaAgent(id={self.id}, name='{self.name}', permission_level='{self.permission_level}')>"


class MetaAgentCommand(BaseModel):
    """
    Command history and tracking table.
    
    Records all commands executed by meta-agents, including parameters,
    execution status, results, and performance metrics.
    """
    __tablename__ = "meta_agent_commands"
    
    # Command identification
    meta_agent_id = Column(Integer, ForeignKey("meta_agents.id"), nullable=False)
    session_id = Column(String(36), nullable=True, index=True)  # UUID for session tracking
    
    # Command details
    command_type = Column(String(50), nullable=False)  # Type of command (e.g., "execute", "query", "orchestrate")
    intent = Column(String(100), nullable=False)  # Classified intent of the command
    parameters = Column(JSON, nullable=True)  # Command parameters
    
    # Execution status
    status = Column(
        Enum(CommandStatus), 
        default=CommandStatus.PENDING, 
        nullable=False
    )
    
    # Results
    result = Column(JSON, nullable=True)  # Execution result
    error_message = Column(Text, nullable=True)  # Error details if failed
    
    # Performance metrics
    execution_time_ms = Column(Float, nullable=True)  # Execution time in milliseconds
    
    # Relationships
    meta_agent = relationship("MetaAgent", back_populates="commands")
    
    def __repr__(self):
        return (
            f"<MetaAgentCommand(id={self.id}, meta_agent_id={self.meta_agent_id}, "
            f"intent='{self.intent}', status='{self.status}')>"
        )


class MetaAgentSession(BaseModel):
    """
    Session management table for meta-agent interactions.
    
    Maintains conversation state and session context for ongoing
    meta-agent interactions.
    """
    __tablename__ = "meta_agent_sessions"
    
    # Session identification
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    meta_agent_id = Column(Integer, ForeignKey("meta_agents.id"), nullable=False, index=True)
    
    # Session status
    status = Column(
        Enum(SessionStatus), 
        default=SessionStatus.ACTIVE, 
        nullable=False
    )
    
    # Session context for maintaining conversation state
    context = Column(JSON, nullable=True)  # Conversation context, variables, history
    
    # Timestamps
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    meta_agent = relationship("MetaAgent", back_populates="sessions")
    
    def __repr__(self):
        return (
            f"<MetaAgentSession(id={self.id}, user_id={self.user_id}, "
            f"meta_agent_id={self.meta_agent_id}, status='{self.status}')>"
        )