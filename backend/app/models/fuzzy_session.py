"""
FUZZY Session Tracking Models

Tracks FUZZY meta-agent sessions and provides comprehensive audit trail
for all studio manipulation operations.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float, DateTime, Enum
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class FuzzyActionType(enum.Enum):
    """Types of actions FUZZY can perform"""
    CREATE_AGENT = "create_agent"
    UPDATE_AGENT = "update_agent"
    DELETE_AGENT = "delete_agent"
    ADD_TOOL = "add_tool"
    REMOVE_TOOL = "remove_tool"
    UPDATE_INSTRUCTIONS = "update_instructions"
    ADD_KNOWLEDGE = "add_knowledge"
    CONFIGURE_CHANNEL = "configure_channel"
    PUBLISH_AGENT = "publish_agent"
    UNPUBLISH_AGENT = "unpublish_agent"
    QUERY_AGENTS = "query_agents"
    QUERY_TOOLS = "query_tools"
    QUERY_INTEGRATIONS = "query_integrations"


class FuzzyActionStatus(enum.Enum):
    """Status of FUZZY action execution"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class FuzzySession(BaseModel):
    """
    FUZZY Session tracking table.
    
    Maintains state for FUZZY meta-agent interactions with the studio.
    """
    __tablename__ = "fuzzy_sessions"
    
    # Session identification
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(100), unique=True, nullable=False, index=True)
    
    # Session state
    is_active = Column(Boolean, default=True, nullable=False)
    context = Column(JSON, nullable=True)  # Conversation context and state
    
    # Session metadata
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    actions = relationship(
        "FuzzyAction",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return (
            f"<FuzzySession(id={self.id}, user_id={self.user_id}, "
            f"session_token='{self.session_token}', is_active={self.is_active})>"
        )


class FuzzyAction(BaseModel):
    """
    FUZZY Action audit trail table.
    
    Records all actions performed by FUZZY for audit and rollback purposes.
    """
    __tablename__ = "fuzzy_actions"
    
    # Action identification
    session_id = Column(Integer, ForeignKey("fuzzy_sessions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Action details
    action_type = Column(Enum(FuzzyActionType), nullable=False, index=True)
    action_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Action parameters and results
    parameters = Column(JSON, nullable=True)  # Input parameters
    result = Column(JSON, nullable=True)  # Action result
    error_message = Column(Text, nullable=True)  # Error details if failed
    
    # Status tracking
    status = Column(
        Enum(FuzzyActionStatus),
        default=FuzzyActionStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Performance metrics
    execution_time_ms = Column(Float, nullable=True)
    
    # Audit trail
    affected_resource_type = Column(String(50), nullable=True)  # e.g., "agent", "tool", "channel"
    affected_resource_id = Column(Integer, nullable=True)  # ID of affected resource
    previous_state = Column(JSON, nullable=True)  # State before action (for rollback)
    new_state = Column(JSON, nullable=True)  # State after action
    
    # Rollback information
    can_rollback = Column(Boolean, default=False, nullable=False)
    rolled_back_at = Column(DateTime(timezone=True), nullable=True)
    rollback_action_id = Column(Integer, ForeignKey("fuzzy_actions.id"), nullable=True)
    
    # Relationships
    session = relationship("FuzzySession", back_populates="actions")
    rollback_action = relationship("FuzzyAction", remote_side="FuzzyAction.id", uselist=False)
    
    def __repr__(self):
        return (
            f"<FuzzyAction(id={self.id}, action_type='{self.action_type}', "
            f"status='{self.status}', user_id={self.user_id})>"
        )


class FuzzyRateLimit(BaseModel):
    """
    Rate limiting table for FUZZY operations.
    
    Prevents abuse by tracking and limiting FUZZY action frequency.
    """
    __tablename__ = "fuzzy_rate_limits"
    
    # Rate limit identification
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Rate limit counters
    actions_count_hourly = Column(Integer, default=0, nullable=False)
    actions_count_daily = Column(Integer, default=0, nullable=False)
    
    # Reset timestamps
    hourly_reset_at = Column(DateTime(timezone=True), nullable=False)
    daily_reset_at = Column(DateTime(timezone=True), nullable=False)
    
    # Limit configuration (can be customized per user)
    hourly_limit = Column(Integer, default=100, nullable=False)
    daily_limit = Column(Integer, default=500, nullable=False)
    
    def __repr__(self):
        return (
            f"<FuzzyRateLimit(user_id={self.user_id}, "
            f"hourly={self.actions_count_hourly}/{self.hourly_limit}, "
            f"daily={self.actions_count_daily}/{self.daily_limit})>"
        )
