"""
FUZZY Tools Pydantic Schemas

Defines request/response schemas for FUZZY studio manipulation tools.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FuzzyActionType(str, Enum):
    """Types of actions FUZZY can perform"""
    CREATE_AGENT = "create_agent"
    UPDATE_AGENT = "update_agent"
    DELETE_AGENT = "delete_agent"
    ADD_TOOL = "add_tool"
    REMOVE_TOOL = "remove_tool"
    UPDATE_INSTRUCTIONS = "update_instructions"
    ADD_KNOWLEDGE = "add_knowledge"
    CONFIGURE_CHANNEL = "configure_channel"
    PUBLISH_AGENT = "publish_agent"
    UNPUBLISH_AGENT = "unpublish_agent"
    QUERY_AGENTS = "query_agents"
    QUERY_TOOLS = "query_tools"
    QUERY_INTEGRATIONS = "query_integrations"


class FuzzyActionStatus(str, Enum):
    """Status of FUZZY action execution"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


# ============== Agent Management Tool Schemas ==============

class CreateAgentRequest(BaseModel):
    """Request schema for creating an agent"""
    name: str = Field(..., description="Name of the agent", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Description of the agent")
    system_prompt: Optional[str] = Field(None, description="System prompt for the agent")
    model_config: Optional[Dict[str, Any]] = Field(None, description="LLM model configuration")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


class UpdateAgentConfigRequest(BaseModel):
    """Request schema for updating agent configuration"""
    agent_id: int = Field(..., description="ID of the agent to update")
    name: Optional[str] = Field(None, description="New name for the agent")
    description: Optional[str] = Field(None, description="New description")
    system_prompt: Optional[str] = Field(None, description="New system prompt")
    model_config: Optional[Dict[str, Any]] = Field(None, description="New model configuration")
    tags: Optional[List[str]] = Field(None, description="New tags")


class DeleteAgentRequest(BaseModel):
    """Request schema for deleting an agent"""
    agent_id: int = Field(..., description="ID of the agent to delete")
    confirm: bool = Field(True, description="Confirmation flag")


class ListUserAgentsRequest(BaseModel):
    """Request schema for listing user's agents"""
    status: Optional[str] = Field(None, description="Filter by status (draft, active, inactive, archived)")
    limit: int = Field(50, description="Maximum number of agents to return", ge=1, le=100)
    offset: int = Field(0, description="Offset for pagination", ge=0)


# ============== Studio Configuration Tool Schemas ==============

class AddToolToAgentRequest(BaseModel):
    """Request schema for adding a tool to an agent"""
    agent_id: int = Field(..., description="ID of the agent")
    tool_name: str = Field(..., description="Name of the tool to add")
    tool_type: str = Field(..., description="Type of tool (e.g., 'function', 'api_call', 'web_scraping')")
    tool_config: Optional[Dict[str, Any]] = Field(None, description="Tool configuration")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Tool parameters")


class RemoveToolFromAgentRequest(BaseModel):
    """Request schema for removing a tool from an agent"""
    agent_id: int = Field(..., description="ID of the agent")
    tool_id: int = Field(..., description="ID of the tool to remove")


class UpdateAgentInstructionsRequest(BaseModel):
    """Request schema for updating agent instructions"""
    agent_id: int = Field(..., description="ID of the agent")
    system_prompt: str = Field(..., description="New system prompt/instructions")
    user_prompt_template: Optional[str] = Field(None, description="User prompt template")


class AddKnowledgeFileRequest(BaseModel):
    """Request schema for adding knowledge file to agent"""
    agent_id: int = Field(..., description="ID of the agent")
    file_name: str = Field(..., description="Name of the knowledge file")
    file_content: Optional[str] = Field(None, description="Content of the file (for text files)")
    file_url: Optional[str] = Field(None, description="URL to the file")
    file_type: str = Field(..., description="Type of file (pdf, txt, docx, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ConfigureCommunicationChannelRequest(BaseModel):
    """Request schema for configuring communication channels"""
    agent_id: int = Field(..., description="ID of the agent")
    channel_type: str = Field(..., description="Type of channel (slack, discord, telegram, etc.)")
    channel_config: Dict[str, Any] = Field(..., description="Channel configuration")
    is_active: bool = Field(True, description="Whether the channel is active")


# ============== Publishing Tool Schemas ==============

class PublishAgentRequest(BaseModel):
    """Request schema for publishing an agent"""
    agent_id: int = Field(..., description="ID of the agent to publish")
    channels: List[str] = Field(..., description="List of channels to publish to")
    publish_config: Optional[Dict[str, Any]] = Field(None, description="Publishing configuration")


class PublishToMarketplaceRequest(BaseModel):
    """Request schema for publishing agent to marketplace"""
    agent_id: int = Field(..., description="ID of the agent to publish")
    marketplace_name: str = Field(..., description="Name for marketplace listing")
    marketplace_description: str = Field(..., description="Description for marketplace")
    category: str = Field(..., description="Category for the agent")
    tags: List[str] = Field(..., description="Tags for marketplace listing")
    pricing_model: str = Field("free", description="Pricing model (free, paid, freemium)")
    price: Optional[float] = Field(None, description="Price if paid model")


class UnpublishAgentRequest(BaseModel):
    """Request schema for unpublishing an agent"""
    agent_id: int = Field(..., description="ID of the agent to unpublish")
    channels: Optional[List[str]] = Field(None, description="Specific channels to unpublish from (None = all)")


# ============== Query Tool Schemas ==============

class GetAgentDetailsRequest(BaseModel):
    """Request schema for getting agent details"""
    agent_id: int = Field(..., description="ID of the agent")


class GetAvailableToolsRequest(BaseModel):
    """Request schema for getting available tools"""
    tool_type: Optional[str] = Field(None, description="Filter by tool type")
    search_query: Optional[str] = Field(None, description="Search query for tools")


class GetAvailableIntegrationsRequest(BaseModel):
    """Request schema for getting available integrations"""
    integration_type: Optional[str] = Field(None, description="Filter by integration type")
    search_query: Optional[str] = Field(None, description="Search query for integrations")


# ============== Response Schemas ==============

class FuzzyToolResponse(BaseModel):
    """Generic response schema for FUZZY tool operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message about the operation")
    data: Optional[Dict[str, Any]] = Field(None, description="Operation result data")
    action_id: Optional[int] = Field(None, description="ID of the action in audit trail")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")


class AgentDetailsResponse(BaseModel):
    """Response schema for agent details"""
    id: int
    name: str
    description: Optional[str]
    status: str
    system_prompt: Optional[str]
    model_config: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    tools: List[Dict[str, Any]]
    knowledge_files: List[Dict[str, Any]]
    communication_channels: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ToolListResponse(BaseModel):
    """Response schema for available tools list"""
    tools: List[Dict[str, Any]]
    total: int


class IntegrationListResponse(BaseModel):
    """Response schema for available integrations list"""
    integrations: List[Dict[str, Any]]
    total: int


class AgentListResponse(BaseModel):
    """Response schema for user's agents list"""
    agents: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int


# ============== Session Schemas ==============

class FuzzySessionCreate(BaseModel):
    """Schema for creating a FUZZY session"""
    context: Optional[Dict[str, Any]] = Field(None, description="Initial session context")


class FuzzySessionResponse(BaseModel):
    """Schema for FUZZY session response"""
    id: int
    user_id: int
    session_token: str
    is_active: bool
    context: Optional[Dict[str, Any]]
    started_at: datetime
    last_activity_at: datetime

    class Config:
        from_attributes = True


# ============== Action Audit Schemas ==============

class FuzzyActionResponse(BaseModel):
    """Schema for FUZZY action audit response"""
    id: int
    session_id: int
    user_id: int
    action_type: FuzzyActionType
    action_name: str
    description: Optional[str]
    parameters: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    status: FuzzyActionStatus
    execution_time_ms: Optional[float]
    affected_resource_type: Optional[str]
    affected_resource_id: Optional[int]
    can_rollback: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FuzzyActionListResponse(BaseModel):
    """Schema for paginated FUZZY action list"""
    actions: List[FuzzyActionResponse]
    total: int
    limit: int
    offset: int


# ============== Rate Limit Schemas ==============

class RateLimitStatus(BaseModel):
    """Schema for rate limit status"""
    user_id: int
    actions_count_hourly: int
    hourly_limit: int
    actions_count_daily: int
    daily_limit: int
    hourly_remaining: int
    daily_remaining: int
    hourly_reset_at: datetime
    daily_reset_at: datetime
