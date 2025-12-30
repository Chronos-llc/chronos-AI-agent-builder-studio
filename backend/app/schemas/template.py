from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


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