"""
FUZZY Tools API Endpoints

RESTful API endpoints for FUZZY meta-agent studio manipulation.
All endpoints require authentication and implement rate limiting.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.core.fuzzy_tools_engine import FuzzyToolsEngine
from app.schemas.fuzzy_tools import (
    CreateAgentRequest, UpdateAgentConfigRequest, DeleteAgentRequest,
    ListUserAgentsRequest, AddToolToAgentRequest, RemoveToolFromAgentRequest,
    UpdateAgentInstructionsRequest, AddKnowledgeFileRequest,
    ConfigureCommunicationChannelRequest, PublishAgentRequest,
    PublishToMarketplaceRequest, UnpublishAgentRequest,
    GetAgentDetailsRequest, GetAvailableToolsRequest, GetAvailableIntegrationsRequest,
    FuzzyToolResponse, AgentDetailsResponse, ToolListResponse,
    IntegrationListResponse, AgentListResponse, FuzzySessionCreate,
    FuzzySessionResponse, FuzzyActionResponse, FuzzyActionListResponse, RateLimitStatus
)

router = APIRouter(prefix="/api/fuzzy-tools", tags=["FUZZY Tools"])


def get_fuzzy_engine(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_fuzzy_session: Optional[str] = Header(None)
) -> FuzzyToolsEngine:
    """Dependency to get FUZZY tools engine instance"""
    return FuzzyToolsEngine(db=db, user_id=current_user.id, session_token=x_fuzzy_session)


# ============== Session Management ==============

@router.post("/sessions", response_model=FuzzySessionResponse)
async def create_fuzzy_session(
    request: FuzzySessionCreate,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Create a new FUZZY session.
    
    Sessions maintain conversation state and context for FUZZY interactions.
    """
    return FuzzySessionResponse(
        id=engine.session.id,
        user_id=engine.session.user_id,
        session_token=engine.session.session_token,
        is_active=engine.session.is_active,
        context=engine.session.context,
        started_at=engine.session.started_at,
        last_activity_at=engine.session.last_activity_at
    )


@router.get("/sessions/current", response_model=FuzzySessionResponse)
async def get_current_session(
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """Get current FUZZY session information"""
    return FuzzySessionResponse(
        id=engine.session.id,
        user_id=engine.session.user_id,
        session_token=engine.session.session_token,
        is_active=engine.session.is_active,
        context=engine.session.context,
        started_at=engine.session.started_at,
        last_activity_at=engine.session.last_activity_at
    )


@router.get("/rate-limit", response_model=RateLimitStatus)
async def get_rate_limit_status(
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """Get current rate limit status for the user"""
    return engine.get_rate_limit_status()


# ============== Agent Management Endpoints ==============

@router.post("/agents/create", response_model=FuzzyToolResponse)
async def create_agent(
    request: CreateAgentRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Create a new agent.
    
    FUZZY uses this endpoint to create agents based on user conversation.
    Requires authentication and respects rate limits.
    """
    return engine.create_agent(request)


@router.put("/agents/update", response_model=FuzzyToolResponse)
async def update_agent_config(
    request: UpdateAgentConfigRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Update agent configuration.
    
    Allows FUZZY to modify agent name, description, system prompt, model config, and tags.
    Only the agent owner can update their agents.
    """
    return engine.update_agent_config(request)


@router.delete("/agents/delete", response_model=FuzzyToolResponse)
async def delete_agent(
    request: DeleteAgentRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Delete an agent.
    
    Permanently removes an agent and all associated data.
    This action cannot be rolled back.
    """
    return engine.delete_agent(request)


@router.get("/agents/list", response_model=AgentListResponse)
async def list_user_agents(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    List user's agents.
    
    Returns paginated list of agents owned by the current user.
    Can filter by status (draft, active, inactive, archived).
    """
    return engine.list_user_agents(status=status, limit=limit, offset=offset)


@router.get("/agents/{agent_id}", response_model=AgentDetailsResponse)
async def get_agent_details(
    agent_id: int,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Get detailed information about an agent.
    
    Returns complete agent configuration including tools, knowledge files,
    and communication channels.
    """
    details = engine.get_agent_details(agent_id)
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found or access denied"
        )
    return details


# ============== Studio Configuration Endpoints ==============

@router.post("/agents/tools/add", response_model=FuzzyToolResponse)
async def add_tool_to_agent(
    request: AddToolToAgentRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Add a tool to an agent.
    
    FUZZY uses this to add capabilities to agents based on user requirements.
    """
    return engine.add_tool_to_agent(request)


@router.delete("/agents/tools/remove", response_model=FuzzyToolResponse)
async def remove_tool_from_agent(
    request: RemoveToolFromAgentRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Remove a tool from an agent.
    
    Removes a specific tool/action from an agent's configuration.
    """
    return engine.remove_tool_from_agent(request)


@router.put("/agents/instructions", response_model=FuzzyToolResponse)
async def update_agent_instructions(
    request: UpdateAgentInstructionsRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Update agent instructions/system prompt.
    
    FUZZY uses this to refine agent behavior based on user feedback.
    """
    return engine.update_agent_instructions(request)


@router.post("/agents/knowledge/add", response_model=FuzzyToolResponse)
async def add_knowledge_file(
    request: AddKnowledgeFileRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Add knowledge file to an agent.
    
    Adds a knowledge base file that the agent can reference.
    """
    return engine.add_knowledge_file(request)


@router.post("/agents/channels/configure", response_model=FuzzyToolResponse)
async def configure_communication_channel(
    request: ConfigureCommunicationChannelRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Configure communication channel for an agent.
    
    Sets up channels like Slack, Discord, Telegram, etc.
    """
    return engine.configure_communication_channel(request)


# ============== Publishing Endpoints ==============

@router.post("/agents/publish", response_model=FuzzyToolResponse)
async def publish_agent(
    request: PublishAgentRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Publish agent to communication channels.
    
    Makes the agent active and available on specified channels.
    """
    return engine.publish_agent(request)


@router.post("/agents/publish/marketplace", response_model=FuzzyToolResponse)
async def publish_to_marketplace(
    request: PublishToMarketplaceRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Publish agent to marketplace.
    
    Lists the agent in the public marketplace for others to discover and use.
    """
    # This would integrate with the marketplace engine
    # For now, return a placeholder response
    return FuzzyToolResponse(
        success=True,
        message=f"Agent published to marketplace (feature in development)",
        data={"agent_id": request.agent_id}
    )


@router.post("/agents/unpublish", response_model=FuzzyToolResponse)
async def unpublish_agent(
    request: UnpublishAgentRequest,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Unpublish agent from channels.
    
    Makes the agent inactive and removes it from specified channels.
    """
    return engine.unpublish_agent(request)


# ============== Query Endpoints ==============

@router.get("/tools/available", response_model=ToolListResponse)
async def get_available_tools(
    tool_type: Optional[str] = None,
    search_query: Optional[str] = None,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Get list of available tools.
    
    Returns tools that can be added to agents.
    Can filter by tool type or search query.
    """
    return engine.get_available_tools(tool_type=tool_type)


@router.get("/integrations/available", response_model=IntegrationListResponse)
async def get_available_integrations(
    integration_type: Optional[str] = None,
    search_query: Optional[str] = None,
    engine: FuzzyToolsEngine = Depends(get_fuzzy_engine)
):
    """
    Get list of available integrations.
    
    Returns integrations that can be configured for agents.
    Can filter by integration type or search query.
    """
    return engine.get_available_integrations(integration_type=integration_type)


# ============== Audit Trail Endpoints ==============

@router.get("/actions/history", response_model=FuzzyActionListResponse)
async def get_action_history(
    limit: int = 50,
    offset: int = 0,
    action_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get action history for the current user.
    
    Returns audit trail of all FUZZY actions performed by the user.
    """
    from app.models.fuzzy_session import FuzzyAction, FuzzyActionType
    from app.schemas.fuzzy_tools import FuzzyActionResponse
    
    query = db.query(FuzzyAction).filter(FuzzyAction.user_id == current_user.id)
    
    if action_type:
        try:
            action_type_enum = FuzzyActionType(action_type)
            query = query.filter(FuzzyAction.action_type == action_type_enum)
        except ValueError:
            pass
    
    total = query.count()
    actions = query.order_by(FuzzyAction.created_at.desc()).offset(offset).limit(limit).all()
    
    actions_data = [
        FuzzyActionResponse(
            id=action.id,
            session_id=action.session_id,
            user_id=action.user_id,
            action_type=action.action_type,
            action_name=action.action_name,
            description=action.description,
            parameters=action.parameters,
            result=action.result,
            error_message=action.error_message,
            status=action.status,
            execution_time_ms=action.execution_time_ms,
            affected_resource_type=action.affected_resource_type,
            affected_resource_id=action.affected_resource_id,
            can_rollback=action.can_rollback,
            created_at=action.created_at
        )
        for action in actions
    ]
    
    return FuzzyActionListResponse(
        actions=actions_data,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/actions/{action_id}", response_model=FuzzyActionResponse)
async def get_action_details(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific action.
    
    Returns complete information about a FUZZY action including
    previous and new states for audit purposes.
    """
    from app.models.fuzzy_session import FuzzyAction
    from app.schemas.fuzzy_tools import FuzzyActionResponse
    from sqlalchemy import and_
    
    action = db.query(FuzzyAction).filter(
        and_(
            FuzzyAction.id == action_id,
            FuzzyAction.user_id == current_user.id
        )
    ).first()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action {action_id} not found"
        )
    
    return FuzzyActionResponse(
        id=action.id,
        session_id=action.session_id,
        user_id=action.user_id,
        action_type=action.action_type,
        action_name=action.action_name,
        description=action.description,
        parameters=action.parameters,
        result=action.result,
        error_message=action.error_message,
        status=action.status,
        execution_time_ms=action.execution_time_ms,
        affected_resource_type=action.affected_resource_type,
        affected_resource_id=action.affected_resource_id,
        can_rollback=action.can_rollback,
        created_at=action.created_at
    )


# ============== Health Check ==============

@router.get("/health")
async def health_check():
    """Health check endpoint for FUZZY tools API"""
    return {
        "status": "healthy",
        "service": "fuzzy-tools",
        "version": "1.0.0"
    }
