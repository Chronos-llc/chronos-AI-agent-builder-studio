from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import (
    Conversation,
    ConversationDialogue,
    DialogueMessage,
    DialogueSession,
    DialogueSessionStatus,
)


DEFAULT_DIALOGUE_MODEL = "gpt-4o"


class AgenticThinkingManager:
    async def start_dialogue(
        self,
        db: AsyncSession,
        *,
        conversation: Conversation,
        prompt: str,
    ) -> DialogueSession:
        session = DialogueSession(
            conversation_id=conversation.id,
            agent_id=conversation.agent_id,
            status=DialogueSessionStatus.ACTIVE,
            model=DEFAULT_DIALOGUE_MODEL,
            started_at=datetime.utcnow(),
        )
        db.add(session)
        await db.flush()

        dialogue_id = f"dlg-{uuid4().hex[:12]}"
        seed_messages = self._build_seed_dialogue(prompt)
        for role, content in seed_messages:
            db.add(
                DialogueMessage(
                    session_id=session.id,
                    role=role,
                    content=content,
                )
            )
            db.add(
                ConversationDialogue(
                    conversation_id=conversation.id,
                    dialogue_id=dialogue_id,
                    role=role,
                    content=content,
                )
            )

        await db.commit()
        await db.refresh(session)
        return session

    async def stop_dialogue(self, db: AsyncSession, *, session: DialogueSession) -> DialogueSession:
        session.status = DialogueSessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(session)
        return session

    async def get_dialogue_messages(self, db: AsyncSession, *, session: DialogueSession) -> List[DialogueMessage]:
        await db.refresh(session, attribute_names=["messages"])
        return list(session.messages)

    def _build_seed_dialogue(self, prompt: str) -> List[tuple[str, str]]:
        condensed_prompt = prompt.strip()
        if len(condensed_prompt) > 240:
            condensed_prompt = condensed_prompt[:237] + "..."
        return [
            ("orchestrator", f"Task received: {condensed_prompt}"),
            ("analyst", "I will break this down into constraints, dependencies, and success criteria."),
            ("critic", "I will challenge assumptions and identify failure modes before tool execution."),
            ("orchestrator", "Consensus: produce a staged plan, then execute with minimal risk."),
        ]


agentic_thinking_manager = AgenticThinkingManager()

