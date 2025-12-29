from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: AgentStatus = AgentStatus.DRAFT
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentCreate(AgentBase):
    model_config: Optional[Dict[str, Any]] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    model_config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(AgentBase):
    id: int
    model_config: Optional[Dict[str, Any]] = None
    usage_count: int
    success_rate: float
    avg_response_time: float
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentVersionBase(BaseModel):
    version_number: str
    changelog: Optional[str] = None
    is_current: bool = False


class AgentVersionCreate(AgentVersionBase):
    config_snapshot: Dict[str, Any]


class AgentVersionResponse(AgentVersionBase):
    id: int
    config_snapshot: Dict[str, Any]
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActionBase(BaseModel):
    name: str
    description: Optional[str] = None
    action_type: str


class ActionCreate(ActionBase):
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None


class ActionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    action_type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None


class ActionResponse(ActionBase):
    id: int
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True