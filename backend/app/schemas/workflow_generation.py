"""
Workflow Generation Pydantic Schemas

Defines request/response schemas for workflow generation API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """Status of generated workflow"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ExecutionStatus(str, Enum):
    """Status of workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowCategory(str, Enum):
    """Categories for workflow templates"""
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    AUTOMATION = "automation"
    ETL = "etl"
    MACHINE_LEARNING = "machine_learning"
    DOCUMENT_PROCESSING = "document_processing"
    NOTIFICATION = "notification"
    SCHEDULING = "scheduling"
    CUSTOM = "custom"


# ============== WorkflowTemplate Schemas ==============

class WorkflowTemplateBase(BaseModel):
    """Base schema for WorkflowTemplate"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: WorkflowCategory = WorkflowCategory.CUSTOM


class WorkflowTemplateCreate(WorkflowTemplateBase):
    """Schema for creating a new WorkflowTemplate"""
    template_schema: Dict[str, Any] = Field(..., description="Workflow structure definition")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Input parameters schema")
    is_public: bool = Field(False, description="Whether the template is public")


class WorkflowTemplateUpdate(BaseModel):
    """Schema for updating a WorkflowTemplate"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[WorkflowCategory] = None
    template_schema: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class WorkflowTemplateResponse(WorkflowTemplateBase):
    """Schema for WorkflowTemplate response"""
    id: int
    template_schema: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None
    is_public: bool
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowTemplateListResponse(BaseModel):
    """Schema for paginated template list"""
    templates: List[WorkflowTemplateResponse]
    total: int
    limit: int
    offset: int


# ============== GeneratedWorkflow Schemas ==============

class GeneratedWorkflowBase(BaseModel):
    """Base schema for GeneratedWorkflow"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class GeneratedWorkflowCreate(GeneratedWorkflowBase):
    """Schema for creating a new GeneratedWorkflow"""
    template_id: Optional[int] = None
    workflow_schema: Dict[str, Any] = Field(..., description="Generated workflow structure")
    generation_params: Optional[Dict[str, Any]] = Field(None, description="Parameters used for generation")
    status: WorkflowStatus = WorkflowStatus.DRAFT


class GeneratedWorkflowResponse(GeneratedWorkflowBase):
    """Schema for GeneratedWorkflow response"""
    id: int
    template_id: Optional[int] = None
    user_id: int
    workflow_schema: Dict[str, Any]
    generation_params: Optional[Dict[str, Any]] = None
    status: WorkflowStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GeneratedWorkflowListResponse(BaseModel):
    """Schema for paginated generated workflow list"""
    workflows: List[GeneratedWorkflowResponse]
    total: int
    limit: int
    offset: int


# ============== WorkflowExecution Schemas ==============

class WorkflowExecutionBase(BaseModel):
    """Base schema for WorkflowExecution"""
    pass


class WorkflowExecutionCreate(WorkflowExecutionBase):
    """Schema for creating a new WorkflowExecution"""
    generated_workflow_id: int
    input_data: Optional[Dict[str, Any]] = None


class WorkflowExecutionResponse(WorkflowExecutionBase):
    """Schema for WorkflowExecution response"""
    id: int
    generated_workflow_id: int
    status: ExecutionStatus
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== WorkflowPattern Schemas ==============

class WorkflowPatternBase(BaseModel):
    """Base schema for WorkflowPattern"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class WorkflowPatternResponse(WorkflowPatternBase):
    """Schema for WorkflowPattern response"""
    id: int
    pattern_schema: Dict[str, Any]
    usage_count: int
    success_rate: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowPatternListResponse(BaseModel):
    """Schema for pattern list"""
    patterns: List[WorkflowPatternResponse]


# ============== Workflow Generation Request/Response ==============

class WorkflowGenerationRequest(BaseModel):
    """Schema for AI-powered workflow generation request"""
    description: str = Field(..., description="Natural language description of the desired workflow")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Input parameters for the workflow")
    category: Optional[WorkflowCategory] = Field(None, description="Optional category hint")


class WorkflowGenerationResponse(BaseModel):
    """Schema for AI-powered workflow generation response"""
    workflow: GeneratedWorkflowResponse
    matched_template: Optional[WorkflowTemplateResponse] = None
    pattern_matches: List[WorkflowPatternResponse] = []
    optimization_suggestions: List[str] = []


class WorkflowExecutionRequest(BaseModel):
    """Schema for executing a generated workflow"""
    workflow_id: int
    input_data: Optional[Dict[str, Any]] = None


class PatternRecognitionRequest(BaseModel):
    """Schema for pattern recognition request"""
    workflow_schema: Dict[str, Any]


class PatternRecognitionResponse(BaseModel):
    """Schema for pattern recognition response"""
    matched_pattern: Optional[WorkflowPatternResponse] = None
    confidence: float = 0.0
    similar_patterns: List[WorkflowPatternResponse] = []


# ============== Workflow Optimization ==============

class WorkflowOptimizationRequest(BaseModel):
    """Schema for workflow optimization request"""
    workflow_schema: Dict[str, Any]


class WorkflowOptimizationResponse(BaseModel):
    """Schema for workflow optimization response"""
    optimized_schema: Dict[str, Any]
    improvements: List[str]
    estimated_performance_gain: float = 0.0
