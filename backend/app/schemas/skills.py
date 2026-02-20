"""
Skills Pydantic Schemas

Defines request and response schemas for skills API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Skill Schemas
class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = Field(None, max_length=50)
    version: Optional[str] = Field(None, max_length=20)
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: bool = True
    is_premium: bool = False


class SkillCreate(SkillBase):
    file_path: str = Field(..., min_length=1, max_length=500)
    content_preview: Optional[str] = None


class SkillUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = Field(None, max_length=50)
    version: Optional[str] = Field(None, max_length=20)
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    file_path: Optional[str] = Field(None, min_length=1, max_length=500)
    content_preview: Optional[str] = None


class SkillResponse(SkillBase):
    id: int
    file_path: str
    file_size: Optional[int] = None
    content_preview: Optional[str] = None
    install_count: int
    download_count: int = 0
    submission_status: Optional[str] = None
    visibility: Optional[str] = None
    published_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    review_notes: Optional[str] = None
    scan_status: Optional[str] = None
    scan_confidence: Optional[int] = None
    scan_summary: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SkillList(BaseModel):
    items: List[SkillResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# Agent Skill Installation Schemas
class AgentSkillInstallationCreate(BaseModel):
    skill_id: int
    configuration: Optional[Dict[str, Any]] = None


class AgentSkillInstallationUpdate(BaseModel):
    configuration: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


class AgentSkillInstallationResponse(BaseModel):
    id: int
    agent_id: int
    skill_id: int
    knowledge_file_id: Optional[int] = None
    configuration: Optional[Dict[str, Any]] = None
    is_enabled: bool
    installed_at: datetime
    created_at: datetime
    updated_at: datetime
    
    # Include skill details
    skill: Optional[SkillResponse] = None
    
    class Config:
        from_attributes = True


class AgentSkillInstallationList(BaseModel):
    items: List[AgentSkillInstallationResponse]
    total: int


# Skill Search and Filter Schemas
class SkillSearchParams(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    sort_by: Optional[str] = "created_at"  # created_at, install_count, name
    sort_order: Optional[str] = "desc"  # asc, desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# Skill Execution Schemas
class SkillExecutionRequest(BaseModel):
    skill_id: int
    parameters: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class SkillExecutionResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


# Skill Statistics Schemas
class SkillStatistics(BaseModel):
    total_skills: int
    active_skills: int
    total_installations: int
    popular_categories: List[Dict[str, Any]]
    recent_skills: List[SkillResponse]
