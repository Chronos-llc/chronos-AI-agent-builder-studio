from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, UTC

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.main import app
from app.models.agent import AgentModel, AgentStatus, AgentType
from app.models.conversation import (
    Conversation,
    ConversationAction,
    ConversationChannelType,
    ConversationMessage,
    ConversationStatus,
)
from app.models.user import User

client = TestClient(app)


def _unique_identity(prefix: str) -> tuple[str, str]:
    token = uuid.uuid4().hex[:10]
    return f"{prefix}.{token}@example.com", f"{prefix}_{token}"


def _register_and_login(email: str, username: str, password: str = "Passw0rd!123") -> str:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
            "password_confirm": password,
        },
    )
    assert register_response.status_code in {200, 201, 400}

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _seed_home_cards_activity(owner_email: str, other_email: str) -> dict[str, int]:
    async with SessionLocal() as db:
        owner = (await db.execute(select(User).where(User.email == owner_email))).scalar_one()
        other = (await db.execute(select(User).where(User.email == other_email))).scalar_one()

        owner_primary = AgentModel(
            name=f"Owner Agent {uuid.uuid4().hex[:6]}",
            description="Primary owner agent",
            status=AgentStatus.ACTIVE,
            agent_type=AgentType.TEXT,
            owner_id=owner.id,
            usage_count=0,
            success_rate=0.0,
            avg_response_time=0.0,
        )
        owner_secondary = AgentModel(
            name=f"Owner Agent {uuid.uuid4().hex[6:12]}",
            description="Secondary owner agent",
            status=AgentStatus.DRAFT,
            agent_type=AgentType.TEXT,
            owner_id=owner.id,
            usage_count=0,
            success_rate=0.0,
            avg_response_time=0.0,
        )
        foreign_agent = AgentModel(
            name=f"Foreign Agent {uuid.uuid4().hex[:6]}",
            description="Different owner",
            status=AgentStatus.ACTIVE,
            agent_type=AgentType.TEXT,
            owner_id=other.id,
            usage_count=0,
            success_rate=0.0,
            avg_response_time=0.0,
        )
        db.add_all([owner_primary, owner_secondary, foreign_agent])
        await db.flush()

        owner_conv_a = Conversation(
            agent_id=owner_primary.id,
            user_id=owner.id,
            channel_type=ConversationChannelType.TELEGRAM,
            status=ConversationStatus.ACTIVE,
            last_message_at=datetime.now(UTC),
        )
        owner_conv_b = Conversation(
            agent_id=owner_primary.id,
            user_id=owner.id,
            channel_type=ConversationChannelType.WEBCHAT,
            status=ConversationStatus.ACTIVE,
            last_message_at=datetime.now(UTC),
        )
        foreign_conv = Conversation(
            agent_id=foreign_agent.id,
            user_id=other.id,
            channel_type=ConversationChannelType.SLACK,
            status=ConversationStatus.ACTIVE,
            last_message_at=datetime.now(UTC),
        )
        db.add_all([owner_conv_a, owner_conv_b, foreign_conv])
        await db.flush()

        db.add_all(
            [
                ConversationMessage(
                    conversation_id=owner_conv_a.id,
                    role="user",
                    content="First user message",
                    tokens_estimate=4,
                ),
                ConversationMessage(
                    conversation_id=owner_conv_a.id,
                    role="agent",
                    content="Agent reply",
                    tokens_estimate=3,
                ),
                ConversationMessage(
                    conversation_id=owner_conv_b.id,
                    role="user",
                    content="Second user message",
                    tokens_estimate=5,
                ),
                ConversationMessage(
                    conversation_id=foreign_conv.id,
                    role="user",
                    content="Foreign message",
                    tokens_estimate=2,
                ),
            ]
        )

        db.add_all(
            [
                ConversationAction(
                    conversation_id=owner_conv_a.id,
                    action_type="http_call",
                    status="failed",
                ),
                ConversationAction(
                    conversation_id=owner_conv_b.id,
                    action_type="db_query",
                    status="error",
                ),
                ConversationAction(
                    conversation_id=owner_conv_b.id,
                    action_type="cache_hit",
                    status="completed",
                ),
                ConversationAction(
                    conversation_id=foreign_conv.id,
                    action_type="foreign_action",
                    status="failed",
                ),
            ]
        )

        await db.commit()
        return {
            "owner_primary_id": owner_primary.id,
            "owner_secondary_id": owner_secondary.id,
            "foreign_agent_id": foreign_agent.id,
        }


def test_agent_home_cards_endpoint_aggregates_live_metrics():
    owner_email, owner_username = _unique_identity("home.owner")
    other_email, other_username = _unique_identity("home.other")

    owner_token = _register_and_login(owner_email, owner_username)
    _register_and_login(other_email, other_username)
    seeded = asyncio.run(_seed_home_cards_activity(owner_email, other_email))

    response = client.get("/api/v1/agents/home/cards", headers=_auth_headers(owner_token))
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["workspace_name"].endswith("'s Workspace")
    assert "generated_at" in payload
    assert "plan" in payload

    agents = payload["agents"]
    returned_ids = {agent["id"] for agent in agents}
    assert seeded["owner_primary_id"] in returned_ids
    assert seeded["owner_secondary_id"] in returned_ids
    assert seeded["foreign_agent_id"] not in returned_ids

    primary = next(agent for agent in agents if agent["id"] == seeded["owner_primary_id"])
    assert primary["messages_received"] == 2
    assert primary["errors_encountered"] == 2
    assert set(primary["deployed_channels"]) == {"telegram", "webchat"}
    assert primary["last_message_at"] is not None

    secondary = next(agent for agent in agents if agent["id"] == seeded["owner_secondary_id"])
    assert secondary["messages_received"] == 0
    assert secondary["errors_encountered"] == 0
    assert secondary["deployed_channels"] == []


def test_agent_home_cards_endpoint_handles_empty_state_and_auth():
    email, username = _unique_identity("home.empty")
    token = _register_and_login(email, username)

    auth_response = client.get("/api/v1/agents/home/cards")
    assert auth_response.status_code in {401, 403}

    response = client.get("/api/v1/agents/home/cards", headers=_auth_headers(token))
    assert response.status_code == 200
    payload = response.json()
    assert payload["agents"] == []
    assert payload["workspace_name"].endswith("'s Workspace")
