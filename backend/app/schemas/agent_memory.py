from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MemoryType(str, Enum):
    """Types of memory storage"""
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    PROCEDURAL = "PROCEDURAL"


class MemoryImportance(str, Enum):
    """Importance levels for memory prioritization"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Memory CRUD Operations
class AgentMemoryCreate(BaseModel):
    """Schema for creating a new memory"""
    content: str = Field(..., min_length=1, description="Memory content")
    summary: Optional[str] = Field(None, max_length=500, description="Brief summary")
    memory_type: MemoryType = Field(default=MemoryType.SHORT_TERM, description="Type of memory")
    importance: MemoryImportance = Field(default=MemoryImportance.MEDIUM, description="Importance level")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration time")


class AgentMemoryUpdate(BaseModel):
    """Schema for updating a memory"""
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    memory_type: Optional[MemoryType] = None
    importance: Optional[MemoryImportance] = None
    context: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class AgentMemoryResponse(BaseModel):
    """Response schema for agent memory"""
    id: int
    agent_id: int
    user_id: int
    memory_type: MemoryType
    importance: MemoryImportance
    content: str
    summary: Optional[str]
    context: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    relevance_score: float
    access_count: int
    last_accessed_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Memory Search and Retrieval
class MemorySearchRequest(BaseModel):
    """Schema for searching memories"""
    query: Optional[str] = Field(None, description="Search query")
    memory_types: Optional[List[MemoryType]] = Field(None, description="Filter by memory types")
    importance_levels: Optional[List[MemoryImportance]] = Field(None, description="Filter by importance")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    min_relevance: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum relevance score")
    include_expired: bool = Field(default=False, description="Include expired memories")
    limit: int = Field(default=50, ge=1, le=500, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class MemorySearchResponse(BaseModel):
    """Response schema for memory search"""
    memories: List[AgentMemoryResponse]
    total: int = Field(..., description="Total number of matching memories")
    limit: int
    offset: int


# Conversation Context Operations
class ConversationContextCreate(BaseModel):
    """Schema for creating conversation context"""
    conversation_id: str = Field(..., min_length=1, max_length=255, description="Unique conversation ID")
    channel: Optional[str] = Field(None, max_length=100, description="Communication channel")
    user_identifier: Optional[str] = Field(None, max_length=255, description="User ID in the channel")
    context_data: Dict[str, Any] = Field(..., description="Conversation state and variables")
    message_history: Optional[List[Dict[str, Any]]] = Field(None, description="Recent message history")


class ConversationContextUpdate(BaseModel):
    """Schema for updating conversation context"""
    context_data: Optional[Dict[str, Any]] = None
    message_history: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class ConversationContextResponse(BaseModel):
    """Response schema for conversation context"""
    id: int
    agent_id: int
    conversation_id: str
    channel: Optional[str]
    user_identifier: Optional[str]
    context_data: Dict[str, Any]
    message_history: Optional[List[Dict[str, Any]]]
    is_active: bool
    last_message_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Memory Statistics
class MemoryStatistics(BaseModel):
    """Statistics about agent memories"""
    total_memories: int
    by_type: Dict[str, int] = Field(..., description="Count by memory type")
    by_importance: Dict[str, int] = Field(..., description="Count by importance level")
    active_memories: int
    expired_memories: int
    avg_relevance_score: float
    most_accessed: List[AgentMemoryResponse] = Field(..., description="Most frequently accessed memories")


# Bulk Operations
class BulkMemoryCreate(BaseModel):
    """Schema for bulk memory creation"""
    memories: List[AgentMemoryCreate] = Field(..., max_items=100, description="List of memories to create")


class BulkMemoryResponse(BaseModel):
    """Response schema for bulk memory operations"""
    created: int = Field(..., description="Number of memories created")
    failed: int = Field(default=0, description="Number that failed")
    errors: Optional[List[str]] = Field(None, description="List of error messages")
