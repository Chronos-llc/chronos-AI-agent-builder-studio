from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class HookType(str, Enum):
    PRE_PROCESS = "pre_process"
    POST_PROCESS = "post_process"
    ERROR_HANDLER = "error_handler"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    MONITORING = "monitoring"
    LOGGING = "logging"


class HookTrigger(str, Enum):
    BEFORE_ACTION = "before_action"
    AFTER_ACTION = "after_action"
    ON_ERROR = "on_error"
    ON_SUCCESS = "on_success"
    ON_TIMEOUT = "on_timeout"
    CUSTOM_EVENT = "custom_event"


class HookStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class HookBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    hook_type: HookType
    trigger: HookTrigger
    status: HookStatus = HookStatus.ACTIVE


class HookCreate(HookBase):
    trigger_conditions: Optional[Dict[str, Any]] = None
    action_config: Dict[str, Any]
    priority: Optional[int] = 0
    is_global: Optional[bool] = False
    dependencies: Optional[List[str]] = None
    timeout: Optional[int] = 10


class HookUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    hook_type: Optional[HookType] = None
    trigger: Optional[HookTrigger] = None
    status: Optional[HookStatus] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    action_config: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    is_global: Optional[bool] = None
    dependencies: Optional[List[str]] = None
    timeout: Optional[int] = None


class HookResponse(HookBase):
    id: int
    trigger_conditions: Optional[Dict[str, Any]] = None
    action_config: Dict[str, Any]
    priority: int
    is_global: bool
    dependencies: Optional[List[str]] = None
    timeout: int
    agent_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HookExecutionRequest(BaseModel):
    hook_id: int
    event_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class HookExecutionResponse(BaseModel):
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: Optional[List[str]] = None
    timestamp: datetime


class HookExecutionLog(BaseModel):
    execution_id: str
    hook_id: int
    status: str
    event_data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float
    timestamp: datetime