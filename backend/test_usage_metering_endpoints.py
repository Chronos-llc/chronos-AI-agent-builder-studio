from __future__ import annotations

import asyncio
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.main import app
from app.models.admin import AdminRole, AdminRoleEnum, AdminUser
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

    login_response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert login_response.status_code == 200, login_response.text
    return login_response.json()["access_token"]


async def _ensure_admin_profile(
    email: str,
    username: str,
    *,
    role_name: AdminRoleEnum = AdminRoleEnum.ADMIN,
    password: str = "Passw0rd!123",
) -> int:
    async with SessionLocal() as db:
        role = (await db.execute(select(AdminRole).where(AdminRole.name == role_name))).scalar_one_or_none()
        if role is None:
            role = AdminRole(
                name=role_name,
                display_name=role_name.value.replace("_", " ").title(),
                description="Seeded in tests",
                is_active=True,
            )
            db.add(role)
            await db.flush()

        user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
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

        admin_user = (await db.execute(select(AdminUser).where(AdminUser.user_id == user.id))).scalar_one_or_none()
        if admin_user is None:
            admin_user = AdminUser(
                user_id=user.id,
                role_id=role.id,
                is_active=True,
            )
            db.add(admin_user)
        else:
            admin_user.role_id = role.id
            admin_user.is_active = True

        await db.commit()
        return user.id


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_usage_resources_and_agent_limit_with_addon():
    email, username = _unique_identity("usage.user")
    token = _register_and_login(email, username)
    headers = _auth_headers(token)

    resources_response = client.get("/api/v1/usage/resources", headers=headers)
    assert resources_response.status_code == 200, resources_response.text
    payload = resources_response.json()
    resource_keys = {item["resource_type"] for item in payload["resources"]}
    assert {"ai_spend", "file_storage", "vector_db_storage", "table_rows", "collaborators", "agents"} <= resource_keys

    create_payload = {
        "name": f"Agent {uuid.uuid4().hex[:6]}",
        "description": "Limit test agent",
        "status": "draft",
        "agent_type": "text",
    }
    first_agent = client.post("/api/v1/agents/", headers=headers, json=create_payload)
    assert first_agent.status_code == 201, first_agent.text

    second_agent = client.post("/api/v1/agents/", headers=headers, json=create_payload)
    assert second_agent.status_code == 429, second_agent.text

    admin_email, admin_username = _unique_identity("usage.admin")
    asyncio.run(_ensure_admin_profile(admin_email, admin_username, role_name=AdminRoleEnum.ADMIN))
    admin_token = _register_and_login(admin_email, admin_username)

    addon_response = client.post(
        "/api/v1/admin/usage/addons",
        headers=_auth_headers(admin_token),
        json={
            "user_id": first_agent.json()["owner_id"],
            "resource_type": "agents",
            "units": 1,
            "unit_price_usd": 10.0,
            "currency": "USD",
        },
    )
    assert addon_response.status_code == 201, addon_response.text

    third_agent = client.post("/api/v1/agents/", headers=headers, json=create_payload)
    assert third_agent.status_code == 201, third_agent.text


def test_admin_balance_adjustment_multi_currency():
    admin_email, admin_username = _unique_identity("balance.admin")
    target_email, target_username = _unique_identity("balance.user")
    asyncio.run(_ensure_admin_profile(admin_email, admin_username, role_name=AdminRoleEnum.ADMIN))

    admin_token = _register_and_login(admin_email, admin_username)
    _register_and_login(target_email, target_username)

    # Resolve target user id from list endpoint.
    users_response = client.get(
        f"/api/payment/balances/users?query={target_username}",
        headers=_auth_headers(admin_token),
    )
    assert users_response.status_code == 200, users_response.text
    items = users_response.json()["items"]
    target_user = next(item for item in items if item["username"] == target_username)
    target_user_id = target_user["user_id"]

    credit_usd = client.post(
        f"/api/payment/balances/users/{target_user_id}/adjust",
        headers=_auth_headers(admin_token),
        json={"currency": "USD", "amount_delta": 120.5, "reason": "Manual credit"},
    )
    assert credit_usd.status_code == 200, credit_usd.text

    debit_ngn = client.post(
        f"/api/payment/balances/users/{target_user_id}/adjust",
        headers=_auth_headers(admin_token),
        json={"currency": "NGN", "amount_delta": -5500, "reason": "Usage debit"},
    )
    assert debit_ngn.status_code == 200, debit_ngn.text
    summary = debit_ngn.json()

    balances = {item["currency"]: item["balance"] for item in summary["balances"]}
    assert balances["USD"] == 120.5
    assert balances["NGN"] == -5500
    assert len(summary["transactions"]) >= 2

