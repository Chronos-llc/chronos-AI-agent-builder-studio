from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.integration import (
    IntegrationResponse,
    IntegrationSubmissionCreate,
    IntegrationSubmissionUpdate,
)


class IntegrationHubListItem(BaseModel):
    id: int
    name: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    integration_type: str
    category: str
    icon: Optional[str] = None
    app_icon_url: Optional[str] = None
    version: str
    status: str
    visibility: str
    download_count: int = 0
    review_count: int = 0
    rating: float = 0.0
    usage_count: int = 0
    active_config_count: int = 0
    total_config_count: int = 0
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    is_workflow_node_enabled: bool = False


class IntegrationHubListResponse(BaseModel):
    items: List[IntegrationHubListItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class IntegrationHubStatisticsResponse(BaseModel):
    integration_id: int
    download_count: int = 0
    review_count: int = 0
    rating: float = 0.0
    active_config_count: int = 0
    total_config_count: int = 0
    usage_count: int = 0
    success_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0


class IntegrationHubCreateRequest(IntegrationSubmissionCreate):
    pass


class IntegrationHubUpdateRequest(IntegrationSubmissionUpdate):
    pass


class IntegrationHubDetailResponse(BaseModel):
    integration: IntegrationResponse

    class Config:
        from_attributes = True


class IntegrationHubMutationResponse(BaseModel):
    integration: IntegrationResponse
    message: str = Field(default="ok")
