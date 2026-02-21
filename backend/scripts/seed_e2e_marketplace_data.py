"""Seed deterministic users and agent records for skills E2E tests."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from sqlalchemy import select

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models.admin import AdminRole, AdminRoleEnum, AdminUser  # noqa: E402
from app.models.agent import AgentModel, AgentStatus  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.user_profile import FuzzyOnboardingState, UserPersona, UserProfile  # noqa: E402


ADMIN_EMAIL = os.getenv("E2E_ADMIN_EMAIL", "e2e.admin@chronos.local")
ADMIN_USERNAME = os.getenv("E2E_ADMIN_USERNAME", "e2e_admin")
ADMIN_PASSWORD = os.getenv("E2E_ADMIN_PASSWORD", "ChronosE2E!123")

USER_EMAIL = os.getenv("E2E_USER_EMAIL", "e2e.user@chronos.local")
USER_USERNAME = os.getenv("E2E_USER_USERNAME", "e2e_user")
USER_PASSWORD = os.getenv("E2E_USER_PASSWORD", "ChronosE2E!123")
AGENT_NAME = os.getenv("E2E_AGENT_NAME", "E2E Skills Agent")


async def _ensure_user(email: str, username: str, password: str) -> User:
    async with SessionLocal() as db:
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

        await db.commit()
        await db.refresh(user)
        return user


async def _ensure_admin_profile(user: User) -> AdminUser:
    async with SessionLocal() as db:
        role = (
            await db.execute(select(AdminRole).where(AdminRole.name == AdminRoleEnum.SUPER_ADMIN))
        ).scalar_one_or_none()
        if role is None:
            role = AdminRole(
                name=AdminRoleEnum.SUPER_ADMIN,
                display_name="Super Admin",
                description="E2E seeded super admin role",
                is_active=True,
            )
            db.add(role)
            await db.flush()

        admin_user = (
            await db.execute(select(AdminUser).where(AdminUser.user_id == user.id))
        ).scalar_one_or_none()
        if admin_user is None:
            admin_user = AdminUser(
                user_id=user.id,
                role_id=role.id,
                is_active=True,
                notes="E2E seed",
            )
            db.add(admin_user)
        else:
            admin_user.role_id = role.id
            admin_user.is_active = True

        await db.commit()
        await db.refresh(admin_user)
        return admin_user


async def _ensure_agent(owner_id: int) -> AgentModel:
    async with SessionLocal() as db:
        agent = (
            await db.execute(
                select(AgentModel).where(
                    AgentModel.owner_id == owner_id,
                    AgentModel.name == AGENT_NAME,
                )
            )
        ).scalar_one_or_none()
        if agent is None:
            agent = AgentModel(
                name=AGENT_NAME,
                description="E2E agent used for skills marketplace flow checks.",
                status=AgentStatus.ACTIVE,
                owner_id=owner_id,
            )
            db.add(agent)
            await db.flush()

        await db.commit()
        await db.refresh(agent)
        return agent


async def _ensure_onboarding_complete(user_id: int) -> UserProfile:
    async with SessionLocal() as db:
        profile = (
            await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        ).scalar_one_or_none()
        if profile is None:
            profile = UserProfile(
                user_id=user_id,
                persona=UserPersona.DEVELOPER,
                onboarding_completed=True,
                fuzzy_onboarding_state=FuzzyOnboardingState.COMPLETED.value,
                primary_goal="Automate recurring workflows",
                use_cases=["automation", "customer-support"],
                tools_stack=["slack", "notion"],
            )
            db.add(profile)
        else:
            profile.persona = profile.persona or UserPersona.DEVELOPER
            profile.onboarding_completed = True
            profile.fuzzy_onboarding_state = FuzzyOnboardingState.COMPLETED.value
            if not profile.primary_goal:
                profile.primary_goal = "Automate recurring workflows"
            profile.use_cases = profile.use_cases or ["automation", "customer-support"]
            profile.tools_stack = profile.tools_stack or ["slack", "notion"]

        await db.commit()
        await db.refresh(profile)
        return profile


async def main() -> dict[str, object]:
    admin_user = await _ensure_user(ADMIN_EMAIL, ADMIN_USERNAME, ADMIN_PASSWORD)
    admin_profile = await _ensure_admin_profile(admin_user)

    regular_user = await _ensure_user(USER_EMAIL, USER_USERNAME, USER_PASSWORD)
    agent = await _ensure_agent(regular_user.id)
    profile = await _ensure_onboarding_complete(regular_user.id)

    payload = {
        "admin": {
            "email": ADMIN_EMAIL,
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "user_id": admin_user.id,
            "admin_user_id": admin_profile.id,
        },
        "user": {
            "email": USER_EMAIL,
            "username": USER_USERNAME,
            "password": USER_PASSWORD,
            "user_id": regular_user.id,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "profile_id": profile.id,
        },
    }
    return payload


if __name__ == "__main__":
    print(json.dumps(asyncio.run(main()), indent=2))
