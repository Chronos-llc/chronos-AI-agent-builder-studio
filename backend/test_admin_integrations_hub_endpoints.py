from __future__ import annotations

import asyncio
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.admin import AdminRole, AdminRoleEnum, AdminUser
from app.models.integration import Integration
from app.models.user import User
from app.main import app

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
                notes="Seeded in tests",
            )
            db.add(admin_user)
            await db.flush()
        else:
            admin_user.role_id = role.id
            admin_user.is_active = True

        await db.commit()
        return user.id


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _integration_create_payload(name: str) -> dict:
    return {
        "name": name,
        "subtitle": "Hub managed integration",
        "description": "Integration created by admin for hub management tests.",
        "integration_type": "mcp_server",
        "category": "automation",
        "visibility": "public",
        "app_icon_url": "",
        "app_screenshots": [],
        "developer_name": "Chronos",
        "website_url": "",
        "support_url_or_email": "",
        "privacy_policy_url": "",
        "terms_url": "",
        "demo_url": "",
        "submission_notes": "seed for admin endpoint test",
        "config_schema": {},
        "credentials_schema": {},
        "supported_features": [],
        "documentation_url": "",
        "version": "1.0.0",
        "is_workflow_node_enabled": False,
    }


def test_admin_integrations_hub_crud_and_stats():
    admin_email, admin_username = _unique_identity("hub.admin")
    asyncio.run(_ensure_admin_profile(admin_email, admin_username, role_name=AdminRoleEnum.ADMIN))
    admin_token = _register_and_login(admin_email, admin_username)
    headers = _auth_headers(admin_token)

    create_response = client.post(
        "/api/v1/admin/integrations/hub",
        headers=headers,
        json=_integration_create_payload(f"hub-int-{uuid.uuid4().hex[:8]}"),
    )
    assert create_response.status_code == 201, create_response.text
    integration = create_response.json()["integration"]
    integration_id = integration["id"]
    assert integration["status"] == "published"

    list_response = client.get("/api/v1/admin/integrations/hub", headers=headers)
    assert list_response.status_code == 200
    assert any(item["id"] == integration_id for item in list_response.json()["items"])

    detail_response = client.get(f"/api/v1/admin/integrations/hub/{integration_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["integration"]["id"] == integration_id

    stats_response = client.get(f"/api/v1/admin/integrations/hub/{integration_id}/statistics", headers=headers)
    assert stats_response.status_code == 200
    stats_payload = stats_response.json()
    for key in [
        "download_count",
        "review_count",
        "rating",
        "active_config_count",
        "total_config_count",
        "usage_count",
        "success_count",
        "error_count",
        "avg_response_time",
    ]:
        assert key in stats_payload

    update_response = client.patch(
        f"/api/v1/admin/integrations/hub/{integration_id}",
        headers=headers,
        json={"description": "Updated by admin endpoint test", "visibility": "private"},
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["integration"]["description"] == "Updated by admin endpoint test"

    delete_response = client.delete(f"/api/v1/admin/integrations/hub/{integration_id}", headers=headers)
    assert delete_response.status_code == 200

    detail_after_delete = client.get(f"/api/v1/admin/integrations/hub/{integration_id}", headers=headers)
    assert detail_after_delete.status_code == 404


def test_admin_integrations_hub_permission_guards():
    admin_email, admin_username = _unique_identity("hub.support")
    user_email, user_username = _unique_identity("hub.user")

    asyncio.run(_ensure_admin_profile(admin_email, admin_username, role_name=AdminRoleEnum.SUPPORT))
    support_token = _register_and_login(admin_email, admin_username)
    user_token = _register_and_login(user_email, user_username)

    support_response = client.get("/api/v1/admin/integrations/hub", headers=_auth_headers(support_token))
    assert support_response.status_code == 403

    user_response = client.get("/api/v1/admin/integrations/hub", headers=_auth_headers(user_token))
    assert user_response.status_code == 403

    anon_response = client.get("/api/v1/admin/integrations/hub")
    assert anon_response.status_code in {401, 403}


def test_admin_integrations_hub_status_filter_and_defaults():
    admin_email, admin_username = _unique_identity("hub.filter")
    asyncio.run(_ensure_admin_profile(admin_email, admin_username, role_name=AdminRoleEnum.ADMIN))
    admin_token = _register_and_login(admin_email, admin_username)
    headers = _auth_headers(admin_token)

    created = client.post(
        "/api/v1/admin/integrations/hub",
        headers=headers,
        json=_integration_create_payload(f"hub-filter-{uuid.uuid4().hex[:8]}"),
    )
    assert created.status_code == 201
    integration_id = created.json()["integration"]["id"]

    # Default filter should emphasize published results.
    default_list = client.get("/api/v1/admin/integrations/hub", headers=headers)
    assert default_list.status_code == 200
    assert any(item["id"] == integration_id for item in default_list.json()["items"])

    all_list = client.get("/api/v1/admin/integrations/hub?status=all", headers=headers)
    assert all_list.status_code == 200
    assert any(item["id"] == integration_id for item in all_list.json()["items"])

    bad_filter = client.get("/api/v1/admin/integrations/hub?status=not_a_status", headers=headers)
    assert bad_filter.status_code == 400

    # Cleanup
    client.delete(f"/api/v1/admin/integrations/hub/{integration_id}", headers=headers)
