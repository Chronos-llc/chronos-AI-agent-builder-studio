from __future__ import annotations

import asyncio
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.database import SessionLocal
from app.core.security import get_password_hash, verify_token
from app.main import app
from app.models.admin import AdminAuditLog, AdminRole, AdminRoleEnum, AdminUser
from app.models.user import User

client = TestClient(app)


def _unique_identity(prefix: str = "user") -> tuple[str, str]:
    token = uuid.uuid4().hex[:8]
    return f"{prefix}_{token}@example.com", f"{prefix}_{token}"


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
        data={
            "username": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    return payload["access_token"]


async def _ensure_admin_profile(email: str, username: str, password: str = "Passw0rd!123") -> None:
    async with SessionLocal() as db:
        role_result = await db.execute(select(AdminRole).where(AdminRole.name == AdminRoleEnum.SUPER_ADMIN))
        role = role_result.scalar_one_or_none()
        if role is None:
            role = AdminRole(
                name=AdminRoleEnum.SUPER_ADMIN,
                display_name="Super Admin",
                description="Seeded in tests",
                is_active=True,
            )
            db.add(role)
            await db.flush()

        user_result = await db.execute(select(User).where(User.email == email))
        user = user_result.scalar_one_or_none()
        if user is None:
            user = User(
                email=email,
                username=username,
                hashed_password=get_password_hash(password),
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.flush()
        else:
            user.username = username
            user.hashed_password = get_password_hash(password)
            user.is_active = True
            user.is_verified = True

        admin_result = await db.execute(select(AdminUser).where(AdminUser.user_id == user.id))
        admin_user = admin_result.scalar_one_or_none()
        if admin_user is None:
            admin_user = AdminUser(
                user_id=user.id,
                role_id=role.id,
                is_active=True,
                notes="Seeded in tests",
            )
            db.add(admin_user)
        else:
            admin_user.role_id = role.id
            admin_user.is_active = True

        await db.commit()


async def _ensure_user_profile_columns() -> None:
    async with SessionLocal() as db:
        table_info = await db.execute(text("PRAGMA table_info(user_profiles)"))
        columns = {row[1] for row in table_info.fetchall()}
        if "fuzzy_onboarding_state" not in columns:
            await db.execute(text("ALTER TABLE user_profiles ADD COLUMN fuzzy_onboarding_state VARCHAR(20) DEFAULT 'pending'"))
        if "fuzzy_onboarding_completed_at" not in columns:
            await db.execute(text("ALTER TABLE user_profiles ADD COLUMN fuzzy_onboarding_completed_at DATETIME"))
        if "fuzzy_onboarding_skipped_at" not in columns:
            await db.execute(text("ALTER TABLE user_profiles ADD COLUMN fuzzy_onboarding_skipped_at DATETIME"))
        await db.execute(
            text(
                "UPDATE user_profiles SET fuzzy_onboarding_state = 'pending' "
                "WHERE fuzzy_onboarding_state IS NULL OR fuzzy_onboarding_state = ''"
            )
        )
        await db.commit()


async def _get_admin_audit_actions(admin_user_id: int) -> list[str]:
    async with SessionLocal() as db:
        result = await db.execute(
            select(AdminAuditLog.action).where(AdminAuditLog.admin_user_id == admin_user_id)
        )
        return [row[0] for row in result.fetchall()]


def test_profile_and_fuzzy_onboarding_lifecycle():
    asyncio.run(_ensure_user_profile_columns())
    email, username = _unique_identity("onboarding")
    token = _register_and_login(email, username)
    headers = {"Authorization": f"Bearer {token}"}

    invalid_profile_response = client.post(
        "/api/v1/users/me/onboarding/profile",
        headers=headers,
        json={
            "persona": "developer",
            "role_title": "Builder",
        },
    )
    assert invalid_profile_response.status_code == 422

    profile_response = client.post(
        "/api/v1/users/me/onboarding/profile",
        headers=headers,
        json={
            "persona": "developer",
            "github_url": "https://github.com/example",
            "role_title": "Builder",
            "company_name": "Chronos",
        },
    )
    assert profile_response.status_code == 200
    profile_payload = profile_response.json()
    assert profile_payload["onboarding_completed"] is True
    assert profile_payload["fuzzy_onboarding_state"] == "pending"

    status_response = client.get("/api/v1/users/me/onboarding/status", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["fuzzy_onboarding_state"] == "pending"

    skip_response = client.post("/api/v1/users/me/onboarding/fuzzy/skip", headers=headers)
    assert skip_response.status_code == 200
    assert skip_response.json()["fuzzy_onboarding_state"] == "skipped"

    fuzzy_response = client.post(
        "/api/v1/users/me/onboarding/fuzzy",
        headers=headers,
        json={
            "primary_goal": "Automate support workflows",
            "use_cases": ["support", "routing"],
            "tools_stack": ["Slack", "Notion"],
        },
    )
    assert fuzzy_response.status_code == 200
    assert fuzzy_response.json()["fuzzy_onboarding_state"] == "completed"


def test_session_context_for_non_admin():
    asyncio.run(_ensure_user_profile_columns())
    email, username = _unique_identity("context")
    token = _register_and_login(email, username)
    response = client.get(
        "/api/v1/auth/session-context",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_admin"] is False
    assert payload["is_impersonating"] is False


def test_admin_switch_profile_and_exit_impersonation():
    asyncio.run(_ensure_user_profile_columns())
    admin_email, admin_username = _unique_identity("admin")
    target_email, target_username = _unique_identity("target")

    asyncio.run(_ensure_admin_profile(admin_email, admin_username))
    _register_and_login(target_email, target_username)
    admin_token = _register_and_login(admin_email, admin_username)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    async def _load_admin_id() -> int:
        async with SessionLocal() as db:
            result = await db.execute(
                select(AdminUser).join(User, AdminUser.user_id == User.id).where(User.email == admin_email)
            )
            admin_profile = result.scalar_one()
            return admin_profile.id

    admin_profile_id = asyncio.run(_load_admin_id())

    blocked_admin_target = client.post(
        "/api/v1/admin/switch-profile/start",
        headers=admin_headers,
        json={"identifier": admin_email},
    )
    assert blocked_admin_target.status_code == 403

    switch_response = client.post(
        "/api/v1/admin/switch-profile/start",
        headers=admin_headers,
        json={"identifier": target_email},
    )
    assert switch_response.status_code == 200
    switched_token = switch_response.json()["access_token"]
    switched_payload = verify_token(switched_token)
    assert switched_payload and switched_payload.get("is_impersonation") is True

    switched_context = client.get(
        "/api/v1/auth/session-context",
        headers={"Authorization": f"Bearer {switched_token}"},
    )
    assert switched_context.status_code == 200
    assert switched_context.json()["is_impersonating"] is True
    assert switched_context.json()["is_admin"] is False

    exit_response = client.post(
        "/api/v1/auth/impersonation/exit",
        headers={"Authorization": f"Bearer {switched_token}"},
    )
    assert exit_response.status_code == 200
    restored_token = exit_response.json()["access_token"]

    restored_context = client.get(
        "/api/v1/auth/session-context",
        headers={"Authorization": f"Bearer {restored_token}"},
    )
    assert restored_context.status_code == 200
    assert restored_context.json()["is_impersonating"] is False
    assert restored_context.json()["is_admin"] is True

    audit_actions = asyncio.run(_get_admin_audit_actions(admin_profile_id))
    assert "switch_profile_start" in audit_actions
    assert "switch_profile_exit" in audit_actions
