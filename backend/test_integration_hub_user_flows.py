from __future__ import annotations

import asyncio
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.main import app
from app.models.integration import Integration, IntegrationConfig, IntegrationStatus, IntegrationVisibility
from app.models.usage import PlanType, UserPlan
from app.models.user import User
from scripts.initialize_mcp_integrations import create_mcp_integrations

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


async def _set_plan(email: str, plan_type: PlanType) -> None:
    async with SessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == email))).scalar_one()
        plan = (await db.execute(select(UserPlan).where(UserPlan.user_id == user.id))).scalar_one_or_none()
        if not plan:
            plan = UserPlan(user_id=user.id, plan_type=plan_type, is_active=True)
            db.add(plan)
        else:
            plan.plan_type = plan_type
            plan.is_active = True
        await db.commit()


async def _seed_user_hub_data(owner_email: str) -> dict[str, int]:
    async with SessionLocal() as db:
        owner = (await db.execute(select(User).where(User.email == owner_email))).scalar_one()

        public_integration = Integration(
            name=f"hub-public-{uuid.uuid4().hex[:8]}",
            description="Public published integration for hub tests",
            integration_type="mcp_server",
            category="automation",
            status=IntegrationStatus.PUBLISHED.value,
            visibility=IntegrationVisibility.PUBLIC.value,
            is_public=True,
            author_id=owner.id,
            config_schema={},
            credentials_schema={},
            supported_features=[],
        )
        team_integration = Integration(
            name=f"hub-team-{uuid.uuid4().hex[:8]}",
            description="Team visibility integration for hub tests",
            integration_type="mcp_server",
            category="automation",
            status=IntegrationStatus.PUBLISHED.value,
            visibility=IntegrationVisibility.TEAM.value,
            is_public=False,
            author_id=owner.id,
            config_schema={},
            credentials_schema={},
            supported_features=[],
        )
        draft_integration = Integration(
            name=f"hub-draft-{uuid.uuid4().hex[:8]}",
            description="Draft integration should never appear in hub",
            integration_type="mcp_server",
            category="automation",
            status=IntegrationStatus.DRAFT.value,
            visibility=IntegrationVisibility.PUBLIC.value,
            is_public=True,
            author_id=owner.id,
            config_schema={},
            credentials_schema={},
            supported_features=[],
        )
        db.add_all([public_integration, team_integration, draft_integration])
        await db.flush()

        db.add(
            IntegrationConfig(
                integration_id=public_integration.id,
                user_id=owner.id,
                config={"enabled": True},
                credentials={},
                is_active=True,
            )
        )
        await db.commit()
        return {
            "public_id": public_integration.id,
            "team_id": team_integration.id,
            "draft_id": draft_integration.id,
        }


def test_user_hub_and_installed_integrations_endpoints():
    email, username = _unique_identity("hub.user")
    token = _register_and_login(email, username)
    ids = asyncio.run(_seed_user_hub_data(email))

    installed_response = client.get("/api/v1/integrations/mine/installed", headers=_auth_headers(token))
    assert installed_response.status_code == 200, installed_response.text
    installed_payload = installed_response.json()
    assert installed_payload["total"] >= 1
    installed_ids = {item["integration_id"] for item in installed_payload["items"]}
    assert ids["public_id"] in installed_ids

    # Free users should only see published public integrations.
    hub_response = client.get("/api/v1/integrations/hub", headers=_auth_headers(token))
    assert hub_response.status_code == 200, hub_response.text
    hub_ids = {item["id"] for item in hub_response.json()}
    assert ids["public_id"] in hub_ids
    assert ids["draft_id"] not in hub_ids
    assert ids["team_id"] not in hub_ids

    asyncio.run(_set_plan(email, PlanType.TEAM_DEVELOPER))
    team_hub_response = client.get("/api/v1/integrations/hub", headers=_auth_headers(token))
    assert team_hub_response.status_code == 200
    team_hub_ids = {item["id"] for item in team_hub_response.json()}
    assert ids["team_id"] in team_hub_ids


def test_seed_upsert_normalizes_existing_records_without_duplicates():
    bootstrap_email, bootstrap_username = _unique_identity("seed.bootstrap")
    _register_and_login(bootstrap_email, bootstrap_username)

    async def run_case() -> None:
        async with SessionLocal() as db:
            seed_user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
            assert seed_user is not None

            name = f"seed-upsert-{uuid.uuid4().hex[:8]}"
            existing = Integration(
                name=name,
                description="legacy draft/private seed",
                integration_type="mcp_server",
                category="automation",
                status=IntegrationStatus.DRAFT.value,
                visibility=IntegrationVisibility.PRIVATE.value,
                is_public=False,
                author_id=seed_user.id,
                config_schema={},
                credentials_schema={},
                supported_features=[],
            )
            db.add(existing)
            await db.commit()

            before_count = len(
                (
                    await db.execute(
                        select(Integration).where(Integration.name == name)
                    )
                ).scalars().all()
            )

            created_1, updated_1 = await create_mcp_integrations(
                db,
                seed_user.id,
                integrations_data=[
                    {
                        "name": name,
                        "description": "normalized",
                        "integration_type": "mcp_server",
                        "category": "automation",
                        "icon": "",
                        "documentation_url": "",
                        "version": "1.0.0",
                        "is_public": True,
                        "config_schema": {},
                        "credentials_schema": {},
                        "supported_features": [],
                    }
                ],
            )
            await db.commit()

            created_2, updated_2 = await create_mcp_integrations(
                db,
                seed_user.id,
                integrations_data=[
                    {
                        "name": name,
                        "description": "normalized",
                        "integration_type": "mcp_server",
                        "category": "automation",
                        "icon": "",
                        "documentation_url": "",
                        "version": "1.0.0",
                        "is_public": True,
                        "config_schema": {},
                        "credentials_schema": {},
                        "supported_features": [],
                    }
                ],
            )
            await db.commit()

            rows = (
                await db.execute(select(Integration).where(Integration.name == name))
            ).scalars().all()
            after_count = len(rows)

            assert created_1 == 0
            assert updated_1 == 1
            assert created_2 == 0
            assert updated_2 == 1
            assert after_count == before_count
            assert rows[0].status == IntegrationStatus.PUBLISHED.value
            assert rows[0].visibility == IntegrationVisibility.PUBLIC.value
            assert rows[0].is_public is True

    asyncio.run(run_case())
