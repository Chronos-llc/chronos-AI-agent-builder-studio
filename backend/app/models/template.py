"""
Template models for the Chronos AI Agent Builder Studio.
Includes both agent templates and workflow templates.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from typing import Dict, Any, Optional
import json

from .base import BaseModel


class TemplateType(str, Enum):
    """Template types supported in the system"""
    AGENT = "agent"
    WORKFLOW = "workflow"
    CHAT_FLOW = "chat_flow"
    AUTOMATION = "automation"
    INTEGRATION = "integration"


class StepType(str, Enum):
    """Types of workflow steps"""
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


class ExecutionStatus(str, Enum):
    """Workflow execution statuses"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class AgentTemplate(BaseModel):
    """Agent template model for creating pre-configured agents"""
    __tablename__ = "agent_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), nullable=False, index=True)
    
    # Template content
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text)
    model_config = Column(JSON)  # Model configuration settings
    tags = Column(JSON)  # List of tags for categorization
    
    # Media and presentation
    preview_image_url = Column(String(500))
    preview_video_url = Column(String(500))
    
    # Usage and ratings
    usage_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Template metadata
    is_featured = Column(Boolean, default=False, index=True)
    is_public = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Creator information
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    
    # Versioning
    version = Column(String(20), default="1.0.0")
    is_latest_version = Column(Boolean, default=True)
    parent_template_id = Column(Integer, ForeignKey("agent_templates.id"))
    
    # Collaboration
    is_collaborative = Column(Boolean, default=False)
    allowed_collaborators = Column(JSON)  # List of user IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Analytics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    fork_count = Column(Integer, default=0)
    
    # Relationships
    categories = relationship("AgentTemplateCategory", secondary="template_category_association")
    versions = relationship("AgentTemplate", remote_side=[id], backref="parent_template")
    
    def __repr__(self):
        return f"<AgentTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"


class AgentTemplateCategory(BaseModel):
    """Category model for organizing agent templates"""
    __tablename__ = "agent_template_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Visual styling
    icon = Column(String(100))  # Icon class or URL
    color = Column(String(20))  # Hex color code
    image_url = Column(String(500))
    
    # Category metadata
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    
    # SEO and discovery
    slug = Column(String(50), unique=True, index=True)
    meta_title = Column(String(200))
    meta_description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    templates = relationship("AgentTemplate", secondary="template_category_association", back_populates="categories")
    
    def __repr__(self):
        return f"<AgentTemplateCategory(id={self.id}, name='{self.name}')>"


# Association table for many-to-many relationship between templates and categories
from .base import Base
from sqlalchemy import Table

template_category_association = Table(
    'template_category_association',
    Base.metadata,
    Column('template_id', Integer, ForeignKey('agent_templates.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('agent_template_categories.id'), primary_key=True)
)


class WorkflowTemplate(BaseModel):
    """Workflow template model for creating complex multi-step workflows"""
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    
    # Template classification
    template_type = Column(SQLEnum(TemplateType), default=TemplateType.WORKFLOW, index=True)
    category = Column(String(50), nullable=False, index=True)
    
    # Workflow definition
    workflow_definition = Column(JSON, nullable=False)  # Complete workflow structure
    step_count = Column(Integer, default=0)
    
    # Template content
    tags = Column(JSON)  # List of tags
    preview_image_url = Column(String(500))
    
    # Usage and ratings
    usage_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Template metadata
    is_featured = Column(Boolean, default=False, index=True)
    is_public = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Complexity and requirements
    complexity_level = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    estimated_duration = Column(Integer)  # Duration in seconds
    required_permissions = Column(JSON)  # Required system permissions
    
    # Creator information
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    
    # Versioning
    version = Column(String(20), default="1.0.0")
    is_latest_version = Column(Boolean, default=True)
    parent_template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    
    # Collaboration
    is_collaborative = Column(Boolean, default=False)
    allowed_collaborators = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Analytics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    fork_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # Success rate of executions
    
    # Relationships
    steps = relationship("WorkflowStep", back_populates="template", cascade="all, delete-orphan")
    versions = relationship("WorkflowTemplate", remote_side=[id], backref="parent_template")
    executions = relationship("WorkflowExecution", back_populates="template")
    analytics = relationship("WorkflowAnalytics", back_populates="template")
    
    def __repr__(self):
        return f"<WorkflowTemplate(id={self.id}, name='{self.name}', type='{self.template_type}')>"


class WorkflowStep(BaseModel):
    """Individual steps within a workflow template"""
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False, index=True)
    
    # Step configuration
    name = Column(String(100), nullable=False)
    description = Column(Text)
    step_type = Column(SQLEnum(StepType), nullable=False, index=True)
    
    # Step definition
    step_config = Column(JSON, nullable=False)  # Step-specific configuration
    input_schema = Column(JSON)  # Expected input format
    output_schema = Column(JSON)  # Expected output format
    
    # Flow control
    order_index = Column(Integer, nullable=False)
    is_parallel = Column(Boolean, default=False)
    condition_expression = Column(Text)  # Conditional execution logic
    
    # Error handling
    retry_count = Column(Integer, default=0)
    timeout_seconds = Column(Integer, default=300)
    failure_action = Column(String(50))  # fail, retry, skip, continue
    
    # Step metadata
    is_optional = Column(Boolean, default=False)
    is_test_step = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="steps")
    executions = relationship("WorkflowStepExecution", back_populates="step")
    
    def __repr__(self):
        return f"<WorkflowStep(id={self.id}, name='{self.name}', type='{self.step_type}')>"


class WorkflowExecution(BaseModel):
    """Track individual workflow executions"""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False, index=True)
    
    # Execution metadata
    execution_name = Column(String(100))  # User-provided name
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    
    # Execution context
    input_data = Column(JSON)  # Input parameters for the workflow
    output_data = Column(JSON)  # Final output of the workflow
    execution_context = Column(JSON)  # Runtime context and variables
    
    # Performance metrics
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Error information
    error_message = Column(Text)
    error_step_id = Column(Integer, ForeignKey("workflow_steps.id"))
    
    # Trigger information
    trigger_type = Column(String(50))  # manual, webhook, schedule, event
    trigger_config = Column(JSON)
    
    # User and source
    triggered_by_user_id = Column(Integer, ForeignKey("users.id"))
    triggered_by = relationship("User", foreign_keys=[triggered_by_user_id])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="executions")
    step_executions = relationship("WorkflowStepExecution", back_populates="execution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkflowExecution(id={self.id}, template_id={self.template_id}, status='{self.status}')>"


class WorkflowStepExecution(BaseModel):
    """Track individual step executions within a workflow"""
    __tablename__ = "workflow_step_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False, index=True)
    step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=False, index=True)
    
    # Step execution details
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)
    attempt_number = Column(Integer, default=1)
    
    # Step data
    input_data = Column(JSON)
    output_data = Column(JSON)
    step_output = Column(Text)  # Text output from the step
    
    # Performance
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    retry_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    execution = relationship("WorkflowExecution", back_populates="step_executions")
    step = relationship("WorkflowStep", back_populates="executions")
    
    def __repr__(self):
        return f"<WorkflowStepExecution(id={self.id}, execution_id={self.execution_id}, step_id={self.step_id})>"


class WorkflowVersion(BaseModel):
    """Version control for workflow templates"""
    __tablename__ = "workflow_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False, index=True)
    
    # Version information
    version_number = Column(String(20), nullable=False)
    version_name = Column(String(100))  # Human-readable version name
    change_log = Column(Text)
    
    # Template snapshot
    template_snapshot = Column(JSON, nullable=False)  # Complete template at this version
    
    # Version metadata
    is_stable = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)
    
    # Creator information
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    template = relationship("WorkflowTemplate")
    
    def __repr__(self):
        return f"<WorkflowVersion(id={self.id}, template_id={self.template_id}, version='{self.version_number}')>"


class WorkflowAnalytics(BaseModel):
    """Analytics and performance tracking for workflow templates"""
    __tablename__ = "workflow_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False, index=True)
    
    # Time period
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Usage metrics
    execution_count = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    
    # Performance metrics
    average_duration = Column(Float, default=0.0)
    total_duration = Column(Integer, default=0)  # Total duration in seconds
    
    # Error metrics
    error_rate = Column(Float, default=0.0)
    most_common_error = Column(String(200))
    
    # User engagement
    unique_users = Column(Integer, default=0)
    return_users = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="analytics")
    
    def __repr__(self):
        return f"<WorkflowAnalytics(id={self.id}, template_id={self.template_id}, date='{self.date}')>"


class TemplateRating(BaseModel):
    """User ratings and reviews for templates"""
    __tablename__ = "template_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, nullable=False, index=True)
    template_type = Column(SQLEnum(TemplateType), nullable=False)
    
    # Rating details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text)
    
    # Review metadata
    is_verified_purchase = Column(Boolean, default=False)
    is_helpful_votes = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<TemplateRating(id={self.id}, template_id={self.template_id}, rating={self.rating})>"