from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConversationCreateRequest(BaseModel):
    agent_id: int
    channel_type: str = Field(default="webchat")
    external_conversation_id: Optional[str] = None
    title: Optional[str] = None
    context_tokens_max: Optional[int] = Field(default=None, ge=1024, le=2_000_000)


class ConversationContinueOnWebResponse(BaseModel):
    conversation_id: int
    context_summary: Optional[str] = None
    context_tokens_used: int
    context_tokens_max: int
    messages: List["ConversationMessageResponse"]


class ConversationResponse(BaseModel):
    id: int
    agent_id: int
    user_id: int
    channel_type: str
    external_conversation_id: Optional[str] = None
    title: Optional[str] = None
    status: str
    last_message_at: Optional[datetime] = None
    context_summary: Optional[str] = None
    context_tokens_used: int
    context_tokens_max: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationMessageCreate(BaseModel):
    role: str = Field(..., pattern="^(user|agent|system)$")
    content: str
    metadata: Optional[Dict[str, Any]] = None
    source_platform_message_id: Optional[str] = None


class ConversationMessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    tokens_estimate: int
    source_platform_message_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationActionResponse(BaseModel):
    id: int
    conversation_id: int
    action_type: str
    payload: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDialogueResponse(BaseModel):
    id: int
    conversation_id: int
    dialogue_id: str
    role: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


ConversationContinueOnWebResponse.model_rebuild()

