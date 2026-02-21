from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.conversation_manager import append_message, get_or_create_conversation
from app.core.database import get_db
from app.models.agent import AgentModel
from app.models.conversation import (
    Conversation,
    ConversationAction,
    ConversationChannelType,
    ConversationDialogue,
    ConversationMessage,
)
from app.models.user import User
from app.schemas.conversation import (
    ConversationActionResponse,
    ConversationContinueOnWebResponse,
    ConversationCreateRequest,
    ConversationDialogueResponse,
    ConversationMessageCreate,
    ConversationMessageResponse,
    ConversationResponse,
)

router = APIRouter()


def _to_message_response(message: ConversationMessage) -> ConversationMessageResponse:
    return ConversationMessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        metadata=message.message_metadata,
        tokens_estimate=message.tokens_estimate,
        source_platform_message_id=message.source_platform_message_id,
        created_at=message.created_at,
        updated_at=message.updated_at,
    )


async def _get_user_agent_or_404(db: AsyncSession, user_id: int, agent_id: int) -> AgentModel:
    agent = (
        await db.execute(
            select(AgentModel).where(and_(AgentModel.id == agent_id, AgentModel.owner_id == user_id))
        )
    ).scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


async def _get_conversation_or_404(db: AsyncSession, user_id: int, conversation_id: int) -> Conversation:
    conversation = (
        await db.execute(
            select(Conversation).where(
                and_(Conversation.id == conversation_id, Conversation.user_id == user_id)
            )
        )
    ).scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_user_agent_or_404(db, current_user.id, request.agent_id)
    conversation = await get_or_create_conversation(
        db,
        agent_id=agent.id,
        user_id=current_user.id,
        channel_type=request.channel_type,
        external_conversation_id=request.external_conversation_id,
        title=request.title,
        context_tokens_max=request.context_tokens_max,
    )
    return conversation


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    agent_id: Optional[int] = Query(default=None),
    channel_type: Optional[str] = Query(default=None),
    status_value: Optional[str] = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Conversation).where(Conversation.user_id == current_user.id)
    if agent_id is not None:
        query = query.where(Conversation.agent_id == agent_id)
    if channel_type is not None:
        query = query.where(Conversation.channel_type == ConversationChannelType(channel_type))
    if status_value is not None:
        query = query.where(Conversation.status == status_value)

    rows = (await db.execute(query.order_by(Conversation.updated_at.desc()))).scalars().all()
    return rows


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_conversation_or_404(db, current_user.id, conversation_id)


@router.get("/conversations/{conversation_id}/messages", response_model=list[ConversationMessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = await _get_conversation_or_404(db, current_user.id, conversation_id)
    messages = (
        await db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation.id)
            .order_by(ConversationMessage.created_at.asc())
        )
    ).scalars().all()
    return [_to_message_response(message) for message in messages]


@router.post("/conversations/{conversation_id}/messages", response_model=ConversationMessageResponse)
async def post_conversation_message(
    conversation_id: int,
    request: ConversationMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = await _get_conversation_or_404(db, current_user.id, conversation_id)
    message = await append_message(
        db,
        conversation=conversation,
        role=request.role,
        content=request.content,
        metadata=request.metadata,
        source_platform_message_id=request.source_platform_message_id,
    )
    return _to_message_response(message)


@router.get("/conversations/{conversation_id}/actions", response_model=list[ConversationActionResponse])
async def get_conversation_actions(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = await _get_conversation_or_404(db, current_user.id, conversation_id)
    rows = (
        await db.execute(
            select(ConversationAction)
            .where(ConversationAction.conversation_id == conversation.id)
            .order_by(ConversationAction.created_at.desc())
        )
    ).scalars().all()
    return rows


@router.get("/conversations/{conversation_id}/dialogues", response_model=list[ConversationDialogueResponse])
async def get_conversation_dialogues(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = await _get_conversation_or_404(db, current_user.id, conversation_id)
    rows = (
        await db.execute(
            select(ConversationDialogue)
            .where(ConversationDialogue.conversation_id == conversation.id)
            .order_by(ConversationDialogue.created_at.asc())
        )
    ).scalars().all()
    return rows


@router.post("/conversations/{conversation_id}/continue-on-web", response_model=ConversationContinueOnWebResponse)
async def continue_conversation_on_web(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = await _get_conversation_or_404(db, current_user.id, conversation_id)
    messages = (
        await db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation.id)
            .order_by(ConversationMessage.created_at.asc())
        )
    ).scalars().all()
    return ConversationContinueOnWebResponse(
        conversation_id=conversation.id,
        context_summary=conversation.context_summary,
        context_tokens_used=conversation.context_tokens_used,
        context_tokens_max=conversation.context_tokens_max,
        messages=[_to_message_response(message) for message in messages],
    )
