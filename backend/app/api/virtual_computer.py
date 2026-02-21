from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import timedelta

from app.core.database import get_db
from app.api.auth import get_current_user
from app.core.virtual_computer import get_virtual_computer_manager
from app.models.user import User
from app.models.agent import AgentModel
from app.models.virtual_computer import VirtualComputerConfiguration
from app.schemas.virtual_computer import (
    VirtualComputerConfigCreate,
    VirtualComputerConfigUpdate,
    VirtualComputerConfigResponse,
    VirtualComputerSessionResponse,
    VirtualComputerExecuteRequest,
    VirtualComputerExecuteResponse,
    VirtualComputerMcpProxyRequest
)
from app.core.enhanced_mcp_manager import enhanced_mcp_manager
from app.schemas.mcp_server import MCPFileOperation
from app.core.conversation_manager import append_action
from app.models.conversation import Conversation

router = APIRouter()


async def _get_agent_or_404(agent_id: int, current_user: User, db: AsyncSession) -> AgentModel:
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


async def _get_or_create_config(agent: AgentModel, current_user: User, db: AsyncSession) -> VirtualComputerConfiguration:
    if agent.virtual_computer_configuration:
        return agent.virtual_computer_configuration

    defaults = VirtualComputerConfigCreate()
    config = VirtualComputerConfiguration(
        agent_id=agent.id,
        user_id=current_user.id,
        **defaults.dict()
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


@router.get("/agents/{agent_id}/virtual-computer", response_model=VirtualComputerConfigResponse)
async def get_virtual_computer_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, current_user, db)
    config = await _get_or_create_config(agent, current_user, db)
    return config


@router.put("/agents/{agent_id}/virtual-computer", response_model=VirtualComputerConfigResponse)
async def update_virtual_computer_config(
    agent_id: int,
    config_update: VirtualComputerConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, current_user, db)
    config = await _get_or_create_config(agent, current_user, db)

    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config


@router.post("/agents/{agent_id}/virtual-computer/reset", response_model=VirtualComputerConfigResponse)
async def reset_virtual_computer_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, current_user, db)
    config = await _get_or_create_config(agent, current_user, db)

    defaults = VirtualComputerConfigCreate()
    for field, value in defaults.dict().items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config


@router.post("/agents/{agent_id}/virtual-computer/session", response_model=VirtualComputerSessionResponse)
async def create_virtual_computer_session(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, current_user, db)
    config = await _get_or_create_config(agent, current_user, db)

    if not config.enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Virtual computer is disabled for this agent")

    manager = get_virtual_computer_manager()
    try:
        session = await manager.create_session(
            agent_id=agent.id,
            user_id=current_user.id,
            idle_timeout_seconds=config.idle_timeout_seconds,
            max_runtime_seconds=config.max_runtime_seconds,
            server_ids=config.mcp_server_ids,
            mcp_enabled=config.mcp_enabled
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    expires_at = session.created_at + timedelta(seconds=config.max_runtime_seconds)
    tools = {
        "operations": ["file_operation", "database_query", "web_scraping", "api_request"],
        "server_ids": config.mcp_server_ids or [],
    }
    return VirtualComputerSessionResponse(
        session_id=session.session_id,
        agent_id=agent.id,
        user_id=current_user.id,
        created_at=session.created_at,
        expires_at=expires_at,
        tools=tools
    )


@router.post("/agents/{agent_id}/virtual-computer/execute", response_model=VirtualComputerExecuteResponse)
async def execute_virtual_computer_code(
    agent_id: int,
    request: VirtualComputerExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, current_user, db)
    config = await _get_or_create_config(agent, current_user, db)

    if not config.enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Virtual computer is disabled for this agent")

    manager = get_virtual_computer_manager()
    try:
        result = await manager.execute_python(
            agent_id=agent.id,
            user_id=current_user.id,
            code=request.code,
            inputs=request.inputs,
            session_id=request.session_id,
            idle_timeout_seconds=config.idle_timeout_seconds,
            max_runtime_seconds=config.max_runtime_seconds,
            server_ids=config.mcp_server_ids,
            mcp_enabled=config.mcp_enabled
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    if request.conversation_id:
        conversation = (
            await db.execute(
                select(Conversation).where(
                    and_(
                        Conversation.id == request.conversation_id,
                        Conversation.user_id == current_user.id,
                        Conversation.agent_id == agent.id,
                    )
                )
            )
        ).scalar_one_or_none()
        if conversation:
            await append_action(
                db,
                conversation=conversation,
                action_type="virtual_computer_execute",
                payload={
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "exit_code": result.get("exit_code"),
                    "duration_ms": result.get("duration_ms", 0),
                },
                status="completed" if result.get("exit_code") in (0, None) else "failed",
            )

    return VirtualComputerExecuteResponse(**result)


@router.post("/virtual-computer/mcp-proxy")
async def virtual_computer_mcp_proxy(
    payload: VirtualComputerMcpProxyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        token = request.headers.get("X-Sandbox-Token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing sandbox token")

    manager = get_virtual_computer_manager()
    try:
        token_payload = manager.decode_sandbox_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid sandbox token")

    agent_id = token_payload.get("agent_id")
    user_id = token_payload.get("user_id")
    if not agent_id or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid sandbox token")

    # Ensure agent config allows MCP
    result = await db.execute(select(AgentModel).where(AgentModel.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    config = agent.virtual_computer_configuration
    if not config or not config.enabled or not config.mcp_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MCP tools are disabled for this agent")

    if config.mcp_server_ids and payload.server_id and payload.server_id not in config.mcp_server_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MCP server not allowed")

    try:
        if payload.operation_type == "file_operation":
            operation = MCPFileOperation(**payload.payload)
            return await enhanced_mcp_manager.file_operation(
                operation,
                server_id=payload.server_id,
                group_name=payload.group_name
            )
        if payload.operation_type == "database_query":
            return await enhanced_mcp_manager.database_query(
                query=payload.payload.get("query"),
                database_type=payload.payload.get("database_type"),
                parameters=payload.payload.get("parameters"),
                server_id=payload.server_id,
                group_name=payload.group_name
            )
        if payload.operation_type == "web_scraping":
            return await enhanced_mcp_manager.scrape_website(
                url=payload.payload.get("url"),
                selectors=payload.payload.get("selectors", {}),
                render_javascript=payload.payload.get("render_javascript", False),
                server_id=payload.server_id,
                group_name=payload.group_name
            )
        if payload.operation_type == "api_request":
            return await enhanced_mcp_manager.make_api_request(
                method=payload.payload.get("method", "GET"),
                url=payload.payload.get("url"),
                headers=payload.payload.get("headers"),
                body=payload.payload.get("body"),
                params=payload.payload.get("params"),
                server_id=payload.server_id,
                group_name=payload.group_name
            )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported operation type")
