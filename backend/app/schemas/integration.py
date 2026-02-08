from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IntegrationType(str, Enum):
    API = "api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MCP_SERVER = "mcp_server"
    AI_MODEL = "ai_model"
    COMMUNICATION = "communication"
    WEBCHAT = "webchat"


class IntegrationCategory(str, Enum):
    DATA_SOURCES = "data_sources"
    AI_MODELS = "ai_models"
    COMMUNICATION = "communication"
    AUTOMATION = "automation"
    MONITORING = "monitoring"
    STORAGE = "storage"
    UTILITIES = "utilities"


class IntegrationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    integration_type: IntegrationType
    category: IntegrationCategory
    icon: Optional[str] = None
    documentation_url: Optional[str] = None
    version: str = "1.0.0"
    is_public: bool = True


class IntegrationCreate(IntegrationBase):
    config_schema: Dict[str, Any] = {}
    credentials_schema: Optional[Dict[str, Any]] = None
    supported_features: List[str] = []


class IntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    integration_type: Optional[IntegrationType] = None
    category: Optional[IntegrationCategory] = None
    icon: Optional[str] = None
    documentation_url: Optional[str] = None
    version: Optional[str] = None
    is_public: Optional[bool] = None
    config_schema: Optional[Dict[str, Any]] = None
    credentials_schema: Optional[Dict[str, Any]] = None
    supported_features: Optional[List[str]] = None


class IntegrationResponse(IntegrationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    author_id: int
    download_count: int
    rating: float
    review_count: int

    class Config:
        from_attributes = True


class IntegrationConfig(BaseModel):
    integration_id: int
    config: Dict[str, Any]
    credentials: Optional[Dict[str, Any]] = None
    is_active: bool = True


class IntegrationConfigCreate(IntegrationConfig):
    pass


class IntegrationConfigUpdate(BaseModel):
    config: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class IntegrationConfigResponse(IntegrationConfig):
    id: int
    created_at: datetime
    updated_at: datetime
    agent_id: Optional[int] = None

    class Config:
        from_attributes = True


class IntegrationReview(BaseModel):
    integration_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class IntegrationReviewCreate(IntegrationReview):
    pass


class IntegrationReviewResponse(IntegrationReview):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntegrationUsageStats(BaseModel):
    integration_id: int
    usage_count: int
    success_count: int
    error_count: int
    avg_response_time: float


class IntegrationMarketplaceSearch(BaseModel):
    query: Optional[str] = None
    categories: Optional[List[IntegrationCategory]] = None
    types: Optional[List[IntegrationType]] = None
    min_rating: Optional[float] = None
    sort_by: Optional[str] = "popularity"
    page: int = 1
    page_size: int = 20


class WebChatConfig(BaseModel):
    embed_type: str = "bubble"  # bubble, iframe, standalone, react
    theme: Dict[str, Any] = {
        "primary_color": "#4F46E5",
        "secondary_color": "#1F2937",
        "text_color": "#FFFFFF",
        "background_color": "#FFFFFF"
    }
    position: str = "bottom_right"
    mobile_responsive: bool = True
    accessibility_features: Dict[str, bool] = {
        "high_contrast": False,
        "screen_reader_support": True,
        "keyboard_navigation": True
    }


class AIModelProviderConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    provider_type: str = Field(..., description="openai, anthropic, ollama, custom")
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: str
    max_tokens: int = 4096
    temperature: float = 0.7


class MCPServerConfig(BaseModel):
    server_url: str
    api_key: Optional[str] = None
    supported_operations: List[str] = []
    timeout: int = 30


class CommunicationChannelConfig(BaseModel):
    channel_type: str = Field(..., description="telegram, slack, whatsapp, discord")
    channel_id: str
    webhook_url: Optional[str] = None
    access_token: Optional[str] = None
    bot_token: Optional[str] = None
