from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)


async def purge_due_deleted_users() -> int:
    async with SessionLocal() as db:
        now = datetime.utcnow()
        users = (
            await db.execute(
                select(User).where(
                    User.deleted_at.is_not(None),
                    User.purge_after.is_not(None),
                    User.purge_after <= now,
                )
            )
        ).scalars().all()

        if not users:
            return 0

        for user in users:
            await db.delete(user)
        await db.commit()
        return len(users)


async def retention_loop(poll_seconds: int = 3600) -> None:
    while True:
        try:
            purged = await purge_due_deleted_users()
            if purged:
                logger.info("Purged %s deleted user accounts", purged)
        except Exception:
            logger.exception("Retention purge loop failed")
        await asyncio.sleep(poll_seconds)

