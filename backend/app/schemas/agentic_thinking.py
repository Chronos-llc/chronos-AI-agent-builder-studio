from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AgenticThinkingStartRequest(BaseModel):
    conversation_id: int
    prompt: str = Field(..., min_length=1)


class AgenticThinkingStopRequest(BaseModel):
    session_id: int


class AgenticThinkingSessionResponse(BaseModel):
    session_id: int
    conversation_id: int
    agent_id: int
    status: str
    model: str
    started_at: datetime
    completed_at: Optional[datetime] = None


class AgenticThinkingMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class AgenticThinkingDialogueResponse(BaseModel):
    session: AgenticThinkingSessionResponse
    messages: List[AgenticThinkingMessageResponse]

