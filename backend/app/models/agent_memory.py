from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base


class MemoryType(str, Enum):
    """Types of memory storage"""
    SHORT_TERM = "SHORT_TERM"  # Recent conversation context
    LONG_TERM = "LONG_TERM"  # Persistent facts and knowledge
    EPISODIC = "EPISODIC"  # Specific events and interactions
    SEMANTIC = "SEMANTIC"  # General knowledge and concepts
    PROCEDURAL = "PROCEDURAL"  # How-to knowledge and procedures


class MemoryImportance(str, Enum):
    """Importance levels for memory prioritization"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentMemory(Base):
    """Memory storage for agents to persist contextual information"""
    __tablename__ = "agent_memories"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Memory classification
    memory_type = Column(SQLEnum(MemoryType), nullable=False, default=MemoryType.SHORT_TERM)
    importance = Column(SQLEnum(MemoryImportance), nullable=False, default=MemoryImportance.MEDIUM)
    
    # Memory content
    content = Column(Text, nullable=False)  # The actual memory content
    summary = Column(String(500), nullable=True)  # Brief summary for quick retrieval
    
    # Context and metadata
    context = Column(JSON, nullable=True)  # Additional context (conversation_id, user_info, etc.)
    tags = Column(JSON, nullable=True)  # Tags for categorization
    
    # Retrieval optimization
    embedding = Column(JSON, nullable=True)  # Vector embedding for semantic search
    relevance_score = Column(Float, default=1.0)  # Relevance/importance score
    
    # Memory lifecycle
    access_count = Column(Integer, default=0)  # How many times accessed
    last_accessed_at = Column(DateTime, nullable=True)  # Last access time
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="memories")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_agent_memory_type', 'agent_id', 'memory_type'),
        Index('idx_agent_memory_importance', 'agent_id', 'importance'),
        Index('idx_memory_active', 'agent_id', 'is_active'),
        Index('idx_memory_created', 'agent_id', 'created_at'),
    )


class ConversationContext(Base):
    """Stores conversation-specific context for agents"""
    __tablename__ = "conversation_contexts"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    
    # Conversation identification
    conversation_id = Column(String(255), nullable=False)  # Unique conversation identifier
    channel = Column(String(100), nullable=True)  # Communication channel (telegram, slack, etc.)
    user_identifier = Column(String(255), nullable=True)  # User ID in the channel
    
    # Context data
    context_data = Column(JSON, nullable=False)  # Conversation state and variables
    message_history = Column(JSON, nullable=True)  # Recent message history
    
    # Metadata
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="conversation_contexts")
    
    # Indexes
    __table_args__ = (
        Index('idx_conversation_id', 'agent_id', 'conversation_id', unique=True),
        Index('idx_conversation_active', 'agent_id', 'is_active'),
        Index('idx_conversation_last_message', 'agent_id', 'last_message_at'),
    )
