from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    FUNCTION = "function"
    API_CALL = "api_call"
    WEB_SCRAPING = "web_scraping"
    CODE_EXECUTION = "code_execution"
    DATA_PROCESSING = "data_processing"
    INTEGRATION = "integration"
    CUSTOM = "custom"


class ActionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ActionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    action_type: ActionType
    status: ActionStatus = ActionStatus.DRAFT


class ActionCreate(ActionBase):
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    timeout: Optional[int] = 30
    retry_policy: Optional[Dict[str, Any]] = None


class ActionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    action_type: Optional[ActionType] = None
    status: Optional[ActionStatus] = None
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    timeout: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None


class ActionResponse(ActionBase):
    id: int
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    timeout: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None
    agent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionExecutionRequest(BaseModel):
    action_id: int
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None


class ActionExecutionResponse(BaseModel):
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: Optional[List[str]] = None
    metrics: Optional[Dict[str, Any]] = None
    timestamp: datetime


class ActionExecutionLog(BaseModel):
    execution_id: str
    action_id: int
    status: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float
    timestamp: datetime
    metrics: Optional[Dict[str, Any]] = None