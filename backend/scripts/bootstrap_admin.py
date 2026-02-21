import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from sqlalchemy import select

# Ensure `app` package resolves whether script is run from repo root or backend dir.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.admin import AdminUser, AdminRole, AdminRoleEnum


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update a Chronos admin account.")
    parser.add_argument("--email", required=True, help="Admin user email")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--full-name", default=None, help="Admin full name")
    parser.add_argument(
        "--role",
        default="super_admin",
        choices=[r.value for r in AdminRoleEnum],
        help="Admin role",
    )
    return parser.parse_args()


async def ensure_role(db, role_name: AdminRoleEnum) -> AdminRole:
    result = await db.execute(select(AdminRole).where(AdminRole.name == role_name))
    role = result.scalar_one_or_none()
    if role:
        return role

    display_map = {
        AdminRoleEnum.SUPER_ADMIN: "Super Admin",
        AdminRoleEnum.ADMIN: "Admin",
        AdminRoleEnum.MODERATOR: "Moderator",
        AdminRoleEnum.SUPPORT: "Support",
    }
    role = AdminRole(
        name=role_name,
        display_name=display_map[role_name],
        description=f"Bootstrapped {role_name.value} role",
        is_active=True,
    )
    db.add(role)
    await db.flush()
    return role


async def bootstrap_admin(
    email: str,
    username: str,
    password: str,
    full_name: Optional[str],
    role: str,
) -> None:
    role_enum = AdminRoleEnum(role)
    async with SessionLocal() as db:
        role_obj = await ensure_role(db, role_enum)

        user_result = await db.execute(
            select(User).where((User.email == email) | (User.username == username))
        )
        user = user_result.scalar_one_or_none()
        created_user = False

        if not user:
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=get_password_hash(password),
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.flush()
            created_user = True
        else:
            user.email = email
            user.username = username
            if full_name is not None:
                user.full_name = full_name
            user.hashed_password = get_password_hash(password)
            user.is_active = True
            user.is_verified = True

        admin_result = await db.execute(select(AdminUser).where(AdminUser.user_id == user.id))
        admin_user = admin_result.scalar_one_or_none()
        created_admin = False

        if not admin_user:
            admin_user = AdminUser(
                user_id=user.id,
                role_id=role_obj.id,
                is_active=True,
                notes="Bootstrapped via script",
            )
            db.add(admin_user)
            created_admin = True
        else:
            admin_user.role_id = role_obj.id
            admin_user.is_active = True

        await db.commit()

        print(f"[OK] User {'created' if created_user else 'updated'}: {email}")
        print(
            f"[OK] Admin profile {'created' if created_admin else 'updated'} with role: {role_obj.name.value}"
        )


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        bootstrap_admin(
            email=args.email.strip().lower(),
            username=args.username.strip(),
            password=args.password,
            full_name=args.full_name.strip() if args.full_name else None,
            role=args.role,
        )
    )
