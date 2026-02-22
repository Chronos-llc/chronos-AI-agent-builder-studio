from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UsageType(str, Enum):
    API_CALL = "api_call"
    STORAGE = "storage"
    AGENT_CREATION = "agent_creation"
    FILE_UPLOAD = "file_upload"


class PlanType(str, Enum):
    FREE = "free"
    LITE = "lite"
    LOTUS = "lotus"
    TEAM_DEVELOPER = "team_developer"
    SPECIAL_SERVICE = "special_service"
    # Legacy value retained for compatibility while data is migrated.
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UsageRecordBase(BaseModel):
    usage_type: UsageType
    amount: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    metadata: Optional[Dict[str, Any]] = None


class UsageRecordCreate(UsageRecordBase):
    agent_id: Optional[int] = None


class UsageRecordResponse(UsageRecordBase):
    id: int
    agent_id: Optional[int] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserPlanBase(BaseModel):
    plan_type: PlanType = PlanType.FREE
    is_active: bool = True


class UserPlanCreate(UserPlanBase):
    pass


class UserPlanUpdate(BaseModel):
    plan_type: Optional[PlanType] = None
    is_active: Optional[bool] = None
    max_agents: Optional[int] = None
    max_api_calls_monthly: Optional[int] = None
    max_storage_mb: Optional[int] = None


class UserPlanResponse(UserPlanBase):
    id: int
    max_agents: int
    max_api_calls_monthly: int
    max_storage_mb: int
    current_agents: int
    current_api_calls_month: int
    current_storage_mb: int
    billing_cycle_start: Optional[datetime] = None
    billing_cycle_end: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsageStats(BaseModel):
    total_agents: int
    active_agents: int
    total_api_calls: int
    current_storage_mb: float
    plan_usage_percentages: Dict[str, float]
    can_create_agent: bool
    can_make_api_call: bool
    remaining_api_calls: int
    remaining_agents: int
    remaining_storage_mb: float


class UsageRecordWithAgent(UsageRecordResponse):
    agent_name: Optional[str] = None


class ResourceUsageType(str, Enum):
    AI_SPEND = "ai_spend"
    FILE_STORAGE = "file_storage"
    VECTOR_DB_STORAGE = "vector_db_storage"
    TABLE_ROWS = "table_rows"
    COLLABORATORS = "collaborators"
    AGENTS = "agents"


class ResourceUsageSnapshot(BaseModel):
    resource_type: ResourceUsageType
    unit: str
    current: float
    base_limit: Optional[float] = None
    addon_limit: float = 0
    total_limit: Optional[float] = None
    percent_used: float = 0
    overage_units: float = 0
    estimated_overage_monthly_usd: float = 0


class UsageResourcesResponse(BaseModel):
    plan: str
    resources: list[ResourceUsageSnapshot]
    updated_at: datetime


class AgentUsageResourcesResponse(BaseModel):
    agent_id: int
    plan: str
    resources: list[ResourceUsageSnapshot]
    updated_at: datetime


class AISpendTrackRequest(BaseModel):
    agent_id: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    cost_amount: float = Field(..., ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    tokens: Optional[int] = Field(default=None, ge=0)
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AISpendTrackResponse(BaseModel):
    id: int
    user_id: int
    agent_id: Optional[int] = None
    cost_amount: float
    currency: str
    event_at: datetime


class AddonAllocationBase(BaseModel):
    user_id: int
    resource_type: ResourceUsageType
    units: int = Field(..., ge=1)
    unit_price_usd: float = Field(..., ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class AddonAllocationCreate(AddonAllocationBase):
    pass


class AddonAllocationResponse(BaseModel):
    id: int
    user_id: int
    resource_type: ResourceUsageType
    units: int
    unit_price_usd: float
    currency: str
    is_active: bool
    effective_from: datetime
    effective_to: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
