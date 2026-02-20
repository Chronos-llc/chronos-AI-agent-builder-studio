"""Idempotent seed routine for default marketplace skills."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import and_, select

# Ensure `app` package resolves whether script is run from repo root or backend dir.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
from app.core.object_storage import (
    ObjectStorageError,
    build_skill_object_key,
    get_object_storage_client,
)
from app.models.skills import (
    Skill,
    SkillScanStatus,
    SkillSubmissionStatus,
    SkillVersion,
    SkillVisibility,
)
from app.models.user import User

SEED_ROOT = BACKEND_DIR / "seed_assets" / "skills"
UPLOAD_ROOT = Path("uploads") / "skills"
logger = logging.getLogger(__name__)
object_storage_client = get_object_storage_client()


@dataclass
class ParsedSeedSkill:
    name: str
    display_name: str
    description: str
    version: str
    raw_content: str
    file_name: str
    category: str
    tags: list[str]


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\-_ ]", "", value).strip().lower()
    value = re.sub(r"[\s_]+", "-", value)
    return value[:96]


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    text = content.lstrip("\ufeff")
    if not text.startswith("---\n"):
        return {}, content

    lines = text.splitlines()
    closing_idx: Optional[int] = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            closing_idx = idx
            break
    if closing_idx is None:
        return {}, content

    frontmatter: dict[str, str] = {}
    for line in lines[1:closing_idx]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip().strip("'").strip('"')
        if key:
            frontmatter[key] = value
    body = "\n".join(lines[closing_idx + 1 :]).strip()
    return frontmatter, body


def _derive_display_name(seed_name: str) -> str:
    return seed_name.replace("-", " ").replace("_", " ").strip().title()


def _infer_category(text: str) -> str:
    lower = text.lower()
    if "financial" in lower:
        return "finance"
    if "gmail" in lower or "email" in lower:
        return "communication"
    if "writer" in lower or "skill" in lower:
        return "productivity"
    return "automation"


async def _load_seed_skill(path: Path) -> ParsedSeedSkill:
    raw_content = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, _body = _parse_frontmatter(raw_content)
    raw_name = frontmatter.get("name") or path.stem
    name = _slugify(raw_name)
    display_name = frontmatter.get("display_name") or _derive_display_name(name)
    description = frontmatter.get("description") or "Seeded marketplace skill."
    version = frontmatter.get("version") or "1.0.0"
    category = frontmatter.get("category") or _infer_category(raw_content)
    return ParsedSeedSkill(
        name=name,
        display_name=display_name,
        description=description,
        version=version,
        raw_content=raw_content,
        file_name=path.name,
        category=category,
        tags=["seeded", "marketplace"],
    )


async def seed_skills_marketplace() -> None:
    if not SEED_ROOT.exists():
        return

    storage_ready = False
    if object_storage_client.available:
        try:
            await object_storage_client.ensure_bucket()
            storage_ready = True
        except ObjectStorageError as exc:
            logger.warning("Object storage unavailable for skill seeding; falling back to local files: %s", exc)

    async with SessionLocal() as db:
        owner = (await db.execute(select(User).order_by(User.id.asc()).limit(1))).scalar_one_or_none()
        owner_id = owner.id if owner else None

        for seed_file in sorted(SEED_ROOT.glob("*.md")):
            parsed = await _load_seed_skill(seed_file)
            if not parsed.name:
                continue

            skill = (await db.execute(select(Skill).where(Skill.name == parsed.name))).scalar_one_or_none()
            if not skill:
                skill = Skill(
                    name=parsed.name,
                    display_name=parsed.display_name,
                    description=parsed.description,
                    category=parsed.category,
                    icon="sparkles",
                    version=parsed.version,
                    file_path="",
                    file_size=len(parsed.raw_content.encode("utf-8", errors="ignore")),
                    content_preview=parsed.raw_content[:700],
                    is_active=True,
                    is_premium=False,
                    tags=parsed.tags,
                    created_by=owner_id,
                    submission_status=SkillSubmissionStatus.PUBLISHED,
                    visibility=SkillVisibility.PUBLIC,
                    scan_status=SkillScanStatus.BENIGN,
                    scan_confidence=92,
                    scan_summary="Seeded trusted marketplace skill.",
                    published_at=datetime.utcnow(),
                )
                db.add(skill)
                await db.flush()
            else:
                skill.display_name = parsed.display_name
                skill.description = parsed.description
                skill.category = parsed.category
                skill.tags = parsed.tags
                skill.version = parsed.version
                skill.file_size = len(parsed.raw_content.encode("utf-8", errors="ignore"))
                skill.content_preview = parsed.raw_content[:700]
                skill.submission_status = SkillSubmissionStatus.PUBLISHED
                skill.visibility = SkillVisibility.PUBLIC
                skill.scan_status = SkillScanStatus.BENIGN
                skill.scan_confidence = max(int(skill.scan_confidence or 0), 90)
                skill.scan_summary = skill.scan_summary or "Seeded trusted marketplace skill."
                skill.is_active = True
                if skill.published_at is None:
                    skill.published_at = datetime.utcnow()
                if skill.created_by is None:
                    skill.created_by = owner_id

            existing_version = (
                await db.execute(
                    select(SkillVersion).where(
                        and_(
                            SkillVersion.skill_id == skill.id,
                            SkillVersion.version == parsed.version,
                        )
                    )
                )
            ).scalar_one_or_none()

            raw_bytes = parsed.raw_content.encode("utf-8", errors="ignore")
            sha256 = hashlib.sha256(raw_bytes).hexdigest()
            object_key = build_skill_object_key(
                skill_id=skill.id,
                version=parsed.version,
                sha256=sha256,
                filename=parsed.file_name,
            )
            uploaded_object = None
            if storage_ready:
                try:
                    uploaded_object = await object_storage_client.put_object_bytes(
                        key=object_key,
                        data=raw_bytes,
                        content_type="text/markdown",
                        metadata={"seeded": "true", "skill_name": parsed.name},
                    )
                except ObjectStorageError as exc:
                    logger.warning(
                        "Failed to upload seeded skill '%s' to object storage; using local fallback: %s",
                        parsed.name,
                        exc,
                    )
                    uploaded_object = None

            if uploaded_object:
                file_path_value = uploaded_object.uri
                raw_content_value = ""
                object_payload = {
                    "object_key": uploaded_object.key,
                    "object_size": uploaded_object.size,
                    "object_content_type": uploaded_object.content_type,
                    "object_etag": uploaded_object.etag,
                    "storage_provider": uploaded_object.provider,
                    "storage_bucket": uploaded_object.bucket,
                }
            else:
                target_dir = UPLOAD_ROOT / parsed.name / parsed.version
                target_dir.mkdir(parents=True, exist_ok=True)
                output_path = target_dir / "SKILL.md"
                output_path.write_text(parsed.raw_content, encoding="utf-8")
                file_path_value = str(output_path)
                # Keep transition compatibility for file_path, but never persist raw file payloads in DB.
                raw_content_value = ""
                object_payload = {
                    "object_key": None,
                    "object_size": None,
                    "object_content_type": None,
                    "object_etag": None,
                    "storage_provider": None,
                    "storage_bucket": None,
                }

            if not existing_version:
                await db.execute(
                    SkillVersion.__table__.update()
                    .where(SkillVersion.skill_id == skill.id)
                    .values(is_current=False)
                )
                existing_version = SkillVersion(
                    skill_id=skill.id,
                    version=parsed.version,
                    file_name=parsed.file_name,
                    file_path=file_path_value,
                    file_sha256=sha256,
                    raw_content=raw_content_value,
                    manifest_json={
                        "seeded": True,
                        "skill_name": parsed.name,
                        "version": parsed.version,
                    },
                    is_current=True,
                    scan_status=SkillScanStatus.BENIGN,
                    scan_report_json={
                        "provider": "seed",
                        "status": SkillScanStatus.BENIGN,
                        "summary": "Trusted seeded skill",
                    },
                    created_by=owner_id,
                    **object_payload,
                )
                db.add(existing_version)
                await db.flush()
            else:
                existing_version.file_name = parsed.file_name
                existing_version.file_path = file_path_value
                existing_version.file_sha256 = sha256
                existing_version.raw_content = raw_content_value
                existing_version.is_current = True
                existing_version.scan_status = SkillScanStatus.BENIGN
                existing_version.object_key = object_payload["object_key"]
                existing_version.object_size = object_payload["object_size"]
                existing_version.object_content_type = object_payload["object_content_type"]
                existing_version.object_etag = object_payload["object_etag"]
                existing_version.storage_provider = object_payload["storage_provider"]
                existing_version.storage_bucket = object_payload["storage_bucket"]
                existing_version.scan_report_json = existing_version.scan_report_json or {
                    "provider": "seed",
                    "status": SkillScanStatus.BENIGN,
                    "summary": "Trusted seeded skill",
                }

            skill.file_path = file_path_value
            skill.version = parsed.version

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_skills_marketplace())
