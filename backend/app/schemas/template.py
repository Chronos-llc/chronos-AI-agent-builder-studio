from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class AgentTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=50)
    system_prompt: str = Field(..., min_length=1)
    user_prompt_template: Optional[str] = None
    model_config: Optional[dict] = None
    tags: Optional[List[str]] = None
    preview_image_url: Optional[str] = None


class AgentTemplateCreate(AgentTemplateBase):
    is_featured: bool = False
    is_public: bool = True


class AgentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    model_config: Optional[dict] = None
    tags: Optional[List[str]] = None
    preview_image_url: Optional[str] = None
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None


class AgentTemplateResponse(AgentTemplateBase):
    id: int
    usage_count: int
    average_rating: int
    is_featured: bool
    is_public: bool
    created_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentTemplateCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class AgentTemplateCategoryCreate(AgentTemplateCategoryBase):
    pass


class AgentTemplateCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class AgentTemplateCategoryResponse(AgentTemplateCategoryBase):
    id: int
    template_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentFromTemplate(BaseModel):
    template_id: int
    agent_name: str
    agent_description: Optional[str] = None


# Workflow Template Schemas

class WorkflowTemplateType(str, Enum):
    """Workflow template types"""
    WORKFLOW = "workflow"
    CHAT_FLOW = "chat_flow"
    AUTOMATION = "automation"
    INTEGRATION = "integration"


class StepType(str, Enum):
    """Workflow step types"""
    AI_AGENT = "ai_agent"
    API_CALL = "api_call"
    CONDITION = "condition"
    LOOP = "loop"
    DATA_TRANSFORM = "data_transform"
    NOTIFICATION = "notification"
    DELAY = "delay"
    WEBHOOK = "webhook"
    FILE_OPERATION = "file_operation"
    DATABASE_QUERY = "database_query"


class WorkflowTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    template_type: WorkflowTemplateType = Field(default=WorkflowTemplateType.WORKFLOW)
    category: str = Field(..., min_length=1, max_length=50)
    workflow_definition: Dict[str, Any] = Field(..., description="Complete workflow structure")
    tags: Optional[List[str]] = None
    preview_image_url: Optional[str] = None
    complexity_level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    estimated_duration: Optional[int] = Field(None, description="Duration in seconds")
    required_permissions: Optional[List[str]] = None


class WorkflowTemplateCreate(WorkflowTemplateBase):
    is_featured: bool = False
    is_public: bool = True
    is_collaborative: bool = False
    allowed_collaborators: Optional[List[int]] = None


class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    template_type: Optional[WorkflowTemplateType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    workflow_definition: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    preview_image_url: Optional[str] = None
    complexity_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    estimated_duration: Optional[int] = None
    required_permissions: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None
    is_collaborative: Optional[bool] = None
    allowed_collaborators: Optional[List[int]] = None


class WorkflowTemplateResponse(WorkflowTemplateBase):
    id: int
    step_count: int
    usage_count: int
    average_rating: float
    rating_count: int
    is_featured: bool
    is_public: bool
    is_verified: bool
    created_by_user_id: int
    version: str
    is_latest_version: bool
    is_collaborative: bool
    view_count: int
    download_count: int
    fork_count: int
    success_rate: float
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowStepBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    step_type: StepType = Field(..., description="Type of workflow step")
    step_config: Dict[str, Any] = Field(..., description="Step-specific configuration")
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    order_index: int = Field(..., ge=0, description="Order of execution")
    is_parallel: bool = Field(default=False, description="Can run in parallel with other steps")
    condition_expression: Optional[str] = Field(None, description="Conditional execution logic")
    retry_count: int = Field(default=0, ge=0)
    timeout_seconds: int = Field(default=300, gt=0)
    failure_action: Optional[str] = Field(None, pattern="^(fail|retry|skip|continue)$")
    is_optional: bool = Field(default=False)
    is_test_step: bool = Field(default=False)


class WorkflowStepCreate(WorkflowStepBase):
    template_id: int


class WorkflowStepUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    step_type: Optional[StepType] = None
    step_config: Optional[Dict[str, Any]] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_parallel: Optional[bool] = None
    condition_expression: Optional[str] = None
    retry_count: Optional[int] = Field(None, ge=0)
    timeout_seconds: Optional[int] = Field(None, gt=0)
    failure_action: Optional[str] = Field(None, pattern="^(fail|retry|skip|continue)$")
    is_optional: Optional[bool] = None
    is_test_step: Optional[bool] = None


class WorkflowStepResponse(WorkflowStepBase):
    id: int
    template_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExecutionStatus(str, Enum):
    """Workflow execution statuses"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowExecutionBase(BaseModel):
    execution_name: Optional[str] = Field(None, max_length=100)
    input_data: Optional[Dict[str, Any]] = None
    trigger_type: Optional[str] = Field(None, pattern="^(manual|webhook|schedule|event)$")
    trigger_config: Optional[Dict[str, Any]] = None


class WorkflowExecutionCreate(WorkflowExecutionBase):
    template_id: int


class WorkflowExecutionUpdate(BaseModel):
    status: Optional[ExecutionStatus] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class WorkflowExecutionResponse(WorkflowExecutionBase):
    id: int
    template_id: int
    status: ExecutionStatus
    output_data: Optional[Dict[str, Any]] = None
    execution_context: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    error_step_id: Optional[int] = None
    triggered_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowStepExecutionBase(BaseModel):
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING)
    attempt_number: int = Field(default=1, ge=1)
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    step_output: Optional[str] = None


class WorkflowStepExecutionCreate(WorkflowStepExecutionBase):
    execution_id: int
    step_id: int


class WorkflowStepExecutionUpdate(BaseModel):
    status: Optional[ExecutionStatus] = None
    attempt_number: Optional[int] = Field(None, ge=1)
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    step_output: Optional[str] = None
    error_message: Optional[str] = None
    retry_reason: Optional[str] = None


class WorkflowStepExecutionResponse(WorkflowStepExecutionBase):
    id: int
    execution_id: int
    step_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    retry_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowVersionBase(BaseModel):
    version_number: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    version_name: Optional[str] = Field(None, max_length=100)
    change_log: Optional[str] = None
    template_snapshot: Dict[str, Any] = Field(..., description="Complete template at this version")
    is_stable: bool = Field(default=True)
    is_deprecated: bool = Field(default=False)


class WorkflowVersionCreate(WorkflowVersionBase):
    template_id: int


class WorkflowVersionResponse(WorkflowVersionBase):
    id: int
    template_id: int
    created_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowAnalyticsBase(BaseModel):
    date: datetime = Field(..., description="Date for analytics")
    execution_count: int = Field(default=0, ge=0)
    successful_executions: int = Field(default=0, ge=0)
    failed_executions: int = Field(default=0, ge=0)
    average_duration: float = Field(default=0.0, ge=0.0)
    total_duration: int = Field(default=0, ge=0)
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    most_common_error: Optional[str] = None
    unique_users: int = Field(default=0, ge=0)
    return_users: int = Field(default=0, ge=0)


class WorkflowAnalyticsCreate(WorkflowAnalyticsBase):
    template_id: int


class WorkflowAnalyticsResponse(WorkflowAnalyticsBase):
    id: int
    template_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateRatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=1000)
    is_verified_purchase: bool = Field(default=False)
    is_helpful_votes: int = Field(default=0, ge=0)


class TemplateRatingCreate(TemplateRatingBase):
    template_id: int
    template_type: WorkflowTemplateType


class TemplateRatingResponse(TemplateRatingBase):
    id: int
    template_id: int
    template_type: WorkflowTemplateType
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Utility schemas

class WorkflowExecutionSummary(BaseModel):
    """Summary of workflow execution for lists"""
    id: int
    execution_name: Optional[str] = None
    template_name: str
    status: ExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    triggered_by: Optional[str] = None


class WorkflowTemplateStats(BaseModel):
    """Statistics for a workflow template"""
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    average_duration: float
    total_users: int
    rating_average: float
    rating_count: int