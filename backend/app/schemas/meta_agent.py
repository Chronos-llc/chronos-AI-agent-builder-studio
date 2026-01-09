"""
Meta-Agent FUZZY Pydantic Schemas

Defines request/response schemas for meta-agent API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PermissionLevel(str, Enum):
    """Permission levels for meta-agent actions"""
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class CommandStatus(str, Enum):
    """Status of meta-agent command execution"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionStatus(str, Enum):
    """Status of meta-agent session"""
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMEOUT = "timeout"


# ============== MetaAgent Schemas ==============

class MetaAgentBase(BaseModel):
    """Base schema for MetaAgent"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class MetaAgentCreate(MetaAgentBase):
    """Schema for creating a new MetaAgent"""
    permission_level: PermissionLevel = PermissionLevel.EDITOR
    allowed_actions: Optional[List[str]] = None
    configuration: Optional[Dict[str, Any]] = None


class MetaAgentUpdate(BaseModel):
    """Schema for updating a MetaAgent"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_level: Optional[PermissionLevel] = None
    allowed_actions: Optional[List[str]] = None
    configuration: Optional[Dict[str, Any]] = None


class MetaAgentResponse(MetaAgentBase):
    """Schema for MetaAgent response"""
    id: int
    permission_level: PermissionLevel
    allowed_actions: Optional[List[str]] = None
    configuration: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== MetaAgentCommand Schemas ==============

class MetaAgentCommandBase(BaseModel):
    """Base schema for MetaAgentCommand"""
    command_type: str
    intent: str
    parameters: Optional[Dict[str, Any]] = None


class MetaAgentCommandCreate(MetaAgentCommandBase):
    """Schema for creating a new MetaAgentCommand"""
    meta_agent_id: int
    session_id: Optional[str] = None


class MetaAgentCommandResponse(MetaAgentCommandBase):
    """Schema for MetaAgentCommand response"""
    id: int
    meta_agent_id: int
    session_id: Optional[str] = None
    status: CommandStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== MetaAgentSession Schemas ==============

class MetaAgentSessionBase(BaseModel):
    """Base schema for MetaAgentSession"""
    pass


class MetaAgentSessionCreate(BaseModel):
    """Schema for creating a new MetaAgentSession"""
    meta_agent_id: int


class MetaAgentSessionResponse(BaseModel):
    """Schema for MetaAgentSession response"""
    id: int
    user_id: int
    meta_agent_id: int
    status: SessionStatus
    context: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============== Command Execution Schemas ==============

class CommandExecutionRequest(BaseModel):
    """Schema for executing a meta-agent command"""
    command: str = Field(..., description="Natural language command to execute")
    parameters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = Field(None, description="Optional session ID for continuing a conversation")


class CommandExecutionResponse(BaseModel):
    """Schema for command execution response"""
    session_id: str
    result: Dict[str, Any]
    execution_time_ms: float
    command_id: Optional[int] = None


# ============== Pagination Schemas ==============

class CommandListResponse(BaseModel):
    """Schema for paginated command list"""
    commands: List[MetaAgentCommandResponse]
    total: int
    limit: int
    offset: int