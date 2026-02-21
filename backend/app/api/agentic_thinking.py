from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.agentic_thinking import agentic_thinking_manager
from app.core.database import get_db
from app.models.agent import AgentModel
from app.models.conversation import Conversation, DialogueSession
from app.models.usage import PlanType, UserPlan
from app.models.user import User
from app.schemas.agentic_thinking import (
    AgenticThinkingDialogueResponse,
    AgenticThinkingSessionResponse,
    AgenticThinkingStartRequest,
    AgenticThinkingStopRequest,
)

router = APIRouter()


def _is_agentic_allowed(user_plan: UserPlan | None) -> bool:
    if not user_plan or not user_plan.is_active:
        return False
    return user_plan.plan_type in {PlanType.PRO, PlanType.ENTERPRISE}


async def _get_agent(db: AsyncSession, user_id: int, agent_id: int) -> AgentModel:
    agent = (
        await db.execute(
            select(AgentModel).where(and_(AgentModel.id == agent_id, AgentModel.owner_id == user_id))
        )
    ).scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


async def _get_conversation(db: AsyncSession, user_id: int, conversation_id: int) -> Conversation:
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


@router.post("/agents/{agent_id}/agentic-thinking/start", response_model=AgenticThinkingDialogueResponse)
async def start_agentic_thinking(
    agent_id: int,
    request: AgenticThinkingStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_plan = (
        await db.execute(select(UserPlan).where(UserPlan.user_id == current_user.id))
    ).scalar_one_or_none()
    if not _is_agentic_allowed(user_plan):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agentic Thinking is available on Pro and Enterprise plans only",
        )

    agent = await _get_agent(db, current_user.id, agent_id)
    conversation = await _get_conversation(db, current_user.id, request.conversation_id)
    if conversation.agent_id != agent.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conversation does not belong to this agent")

    session = await agentic_thinking_manager.start_dialogue(
        db,
        conversation=conversation,
        prompt=request.prompt,
    )
    messages = await agentic_thinking_manager.get_dialogue_messages(db, session=session)
    return AgenticThinkingDialogueResponse(
        session=AgenticThinkingSessionResponse(
            session_id=session.id,
            conversation_id=session.conversation_id,
            agent_id=session.agent_id,
            status=session.status.value if hasattr(session.status, "value") else str(session.status),
            model=session.model,
            started_at=session.started_at,
            completed_at=session.completed_at,
        ),
        messages=messages,
    )


@router.post("/agents/{agent_id}/agentic-thinking/stop", response_model=AgenticThinkingSessionResponse)
async def stop_agentic_thinking(
    agent_id: int,
    request: AgenticThinkingStopRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent(db, current_user.id, agent_id)
    session = (
        await db.execute(
            select(DialogueSession)
            .join(Conversation, Conversation.id == DialogueSession.conversation_id)
            .where(
                DialogueSession.id == request.session_id,
                DialogueSession.agent_id == agent_id,
                Conversation.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dialogue session not found")

    session = await agentic_thinking_manager.stop_dialogue(db, session=session)
    return AgenticThinkingSessionResponse(
        session_id=session.id,
        conversation_id=session.conversation_id,
        agent_id=session.agent_id,
        status=session.status.value if hasattr(session.status, "value") else str(session.status),
        model=session.model,
        started_at=session.started_at,
        completed_at=session.completed_at,
    )

