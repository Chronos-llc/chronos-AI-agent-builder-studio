from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model_catalog import get_context_window_for_model
from app.models.agent import AgentModel
from app.models.conversation import (
    Conversation,
    ConversationAction,
    ConversationChannelType,
    ConversationMessage,
    ConversationStatus,
)


CONTEXT_CONDENSE_THRESHOLD = 0.80
DEFAULT_CONTEXT_WINDOW = 16000
CONTEXT_KEEP_LATEST_MESSAGES = 20


def estimate_tokens(content: str) -> int:
    if not content:
        return 0
    return max(1, len(content) // 4)


def _resolve_channel(channel_type: str | ConversationChannelType) -> ConversationChannelType:
    if isinstance(channel_type, ConversationChannelType):
        return channel_type
    return ConversationChannelType(channel_type)


def _extract_model_name(agent: Optional[AgentModel]) -> Optional[str]:
    if not agent:
        return None
    model_config = agent.model_config or {}
    if isinstance(model_config, dict):
        return model_config.get("llm_model") or model_config.get("model")
    return None


def _build_summary(message_contents: Iterable[str], max_chars: int = 1200) -> str:
    parts = [part.strip() for part in message_contents if part and part.strip()]
    if not parts:
        return ""
    joined = " ".join(parts)
    if len(joined) > max_chars:
        joined = joined[: max_chars - 3] + "..."
    timestamp = datetime.utcnow().isoformat()
    return f"[Context summary @ {timestamp}] {joined}"


async def get_or_create_conversation(
    db: AsyncSession,
    *,
    agent_id: int,
    user_id: int,
    channel_type: str | ConversationChannelType = ConversationChannelType.WEBCHAT,
    external_conversation_id: Optional[str] = None,
    title: Optional[str] = None,
    context_tokens_max: Optional[int] = None,
) -> Conversation:
    channel = _resolve_channel(channel_type)

    query = select(Conversation).where(
        Conversation.agent_id == agent_id,
        Conversation.user_id == user_id,
        Conversation.channel_type == channel,
        Conversation.status == ConversationStatus.ACTIVE,
    )

    if external_conversation_id is None:
        query = query.where(Conversation.external_conversation_id.is_(None))
    else:
        query = query.where(Conversation.external_conversation_id == external_conversation_id)

    existing = (await db.execute(query.order_by(Conversation.updated_at.desc()))).scalars().first()
    if existing:
        return existing

    context_max = context_tokens_max
    if context_max is None:
        agent = await db.get(AgentModel, agent_id)
        model_name = _extract_model_name(agent)
        context_max = get_context_window_for_model(model_name) if model_name else DEFAULT_CONTEXT_WINDOW

    conversation = Conversation(
        agent_id=agent_id,
        user_id=user_id,
        channel_type=channel,
        external_conversation_id=external_conversation_id,
        title=title,
        context_tokens_max=context_max or DEFAULT_CONTEXT_WINDOW,
        context_tokens_used=0,
        status=ConversationStatus.ACTIVE,
        last_message_at=datetime.utcnow(),
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def append_message(
    db: AsyncSession,
    *,
    conversation: Conversation,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    source_platform_message_id: Optional[str] = None,
) -> ConversationMessage:
    tokens = estimate_tokens(content)
    message = ConversationMessage(
        conversation_id=conversation.id,
        role=role,
        content=content,
        message_metadata=metadata,
        tokens_estimate=tokens,
        source_platform_message_id=source_platform_message_id,
    )
    db.add(message)
    conversation.last_message_at = datetime.utcnow()
    conversation.context_tokens_used = (conversation.context_tokens_used or 0) + tokens
    await db.commit()
    await db.refresh(message)
    await db.refresh(conversation)

    await condense_context_if_needed(db, conversation)
    return message


async def append_action(
    db: AsyncSession,
    *,
    conversation: Conversation,
    action_type: str,
    payload: Optional[Dict[str, Any]] = None,
    status: str = "completed",
) -> ConversationAction:
    action = ConversationAction(
        conversation_id=conversation.id,
        action_type=action_type,
        payload=payload,
        status=status,
    )
    db.add(action)
    conversation.last_message_at = datetime.utcnow()
    await db.commit()
    await db.refresh(action)
    return action


async def condense_context_if_needed(db: AsyncSession, conversation: Conversation) -> None:
    max_tokens = conversation.context_tokens_max or DEFAULT_CONTEXT_WINDOW
    used = conversation.context_tokens_used or 0
    if max_tokens <= 0 or used < int(max_tokens * CONTEXT_CONDENSE_THRESHOLD):
        return

    messages = (
        await db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation.id)
            .order_by(ConversationMessage.created_at.asc())
        )
    ).scalars().all()

    if len(messages) <= CONTEXT_KEEP_LATEST_MESSAGES:
        return

    keep_messages = messages[-CONTEXT_KEEP_LATEST_MESSAGES:]
    trim_messages = messages[:-CONTEXT_KEEP_LATEST_MESSAGES]
    summary_max_tokens = 100
    agent = await db.get(AgentModel, conversation.agent_id)
    sub_agent_config = getattr(agent, "sub_agent_config", None) if agent else None
    if isinstance(sub_agent_config, dict):
        summary_cfg = sub_agent_config.get("summary_agent") or {}
        if isinstance(summary_cfg, dict):
            summary_max_tokens = int(summary_cfg.get("summary_max_tokens", summary_max_tokens))

    max_chars = max(200, summary_max_tokens * 4)
    summary = _build_summary((message.content for message in trim_messages), max_chars=max_chars)
    if summary:
        if conversation.context_summary:
            conversation.context_summary = f"{conversation.context_summary}\n{summary}"
        else:
            conversation.context_summary = summary

    trim_ids = [message.id for message in trim_messages]
    if trim_ids:
        await db.execute(
            delete(ConversationMessage).where(
                ConversationMessage.conversation_id == conversation.id,
                ConversationMessage.id.in_(trim_ids),
            )
        )

    remaining_tokens = sum(message.tokens_estimate or 0 for message in keep_messages)
    summary_tokens = estimate_tokens(conversation.context_summary or "")
    conversation.context_tokens_used = remaining_tokens + summary_tokens
    await db.commit()
