"""Backfill legacy file/image records into object storage."""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
from app.core.object_storage import (  # noqa: E402
    ObjectStorageError,
    build_knowledge_object_key,
    build_playwright_screenshot_key,
    build_skill_object_key,
    build_storage_key,
    get_object_storage_client,
    parse_object_uri,
)
from app.models.knowledge import KnowledgeFile  # noqa: E402
from app.models.playwright_enhanced import PlaywrightArtifact, PlaywrightToolExecution  # noqa: E402
from app.models.skills import SkillVersion  # noqa: E402


@dataclass
class BackfillStats:
    scanned: int = 0
    migrated: int = 0
    skipped: int = 0
    failed: int = 0


def _load_bytes_from_legacy_file(path_value: str) -> bytes | None:
    if not path_value:
        return None
    file_path = Path(path_value)
    if file_path.exists() and file_path.is_file():
        return file_path.read_bytes()
    return None


def _content_type_from_name(filename: str, fallback: str = "application/octet-stream") -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".md", ".txt"}:
        return "text/markdown" if suffix == ".md" else "text/plain"
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".gif":
        return "image/gif"
    if suffix == ".webp":
        return "image/webp"
    return fallback


async def backfill_skills(stats: BackfillStats) -> None:
    object_storage_client = get_object_storage_client()
    async with SessionLocal() as db:
        rows = (
            await db.execute(
                select(SkillVersion).where(
                    SkillVersion.object_key.is_(None)
                )
            )
        ).scalars().all()

        for version in rows:
            stats.scanned += 1
            try:
                legacy_uri = parse_object_uri(version.file_path)
                if legacy_uri and not version.object_key:
                    bucket, key = legacy_uri
                    version.object_key = key
                    version.storage_bucket = bucket
                    version.storage_provider = "s3"
                    stats.migrated += 1
                    continue

                raw_content = version.raw_content or ""
                payload = raw_content.encode("utf-8", errors="ignore") if raw_content else None
                if not payload:
                    payload = _load_bytes_from_legacy_file(version.file_path)

                if not payload:
                    stats.skipped += 1
                    continue

                sha256 = hashlib.sha256(payload).hexdigest()
                key = build_skill_object_key(
                    skill_id=version.skill_id,
                    version=version.version,
                    sha256=sha256,
                    filename=version.file_name,
                )
                stored = await object_storage_client.put_object_bytes(
                    key=key,
                    data=payload,
                    content_type="text/markdown",
                    metadata={"domain": "skills", "version_id": str(version.id)},
                )
                version.object_key = stored.key
                version.object_size = stored.size
                version.object_content_type = stored.content_type
                version.object_etag = stored.etag
                version.storage_provider = stored.provider
                version.storage_bucket = stored.bucket
                if version.file_path and not version.file_path.startswith("object://"):
                    version.file_path = stored.uri
                stats.migrated += 1
            except Exception:
                stats.failed += 1

        await db.commit()


async def backfill_knowledge(stats: BackfillStats) -> None:
    object_storage_client = get_object_storage_client()
    async with SessionLocal() as db:
        rows = (
            await db.execute(
                select(KnowledgeFile).where(
                    KnowledgeFile.object_key.is_(None)
                )
            )
        ).scalars().all()

        for row in rows:
            stats.scanned += 1
            try:
                legacy_uri = parse_object_uri(row.file_path)
                if legacy_uri and not row.object_key:
                    bucket, key = legacy_uri
                    row.object_key = key
                    row.storage_bucket = bucket
                    row.storage_provider = "s3"
                    stats.migrated += 1
                    continue

                payload = _load_bytes_from_legacy_file(row.file_path)
                if not payload:
                    stats.skipped += 1
                    continue

                sha256 = hashlib.sha256(payload).hexdigest()
                key = build_knowledge_object_key(
                    agent_id=row.agent_id,
                    knowledge_file_id=row.id,
                    sha256=sha256,
                    filename=row.original_filename,
                )
                stored = await object_storage_client.put_object_bytes(
                    key=key,
                    data=payload,
                    content_type=row.mime_type or _content_type_from_name(row.original_filename),
                    metadata={"domain": "knowledge", "knowledge_file_id": str(row.id)},
                )
                row.object_key = stored.key
                row.object_size = stored.size
                row.object_content_type = stored.content_type
                row.object_etag = stored.etag
                row.storage_provider = stored.provider
                row.storage_bucket = stored.bucket
                if row.file_path and not row.file_path.startswith("object://"):
                    row.file_path = stored.uri
                stats.migrated += 1
            except Exception:
                stats.failed += 1

        await db.commit()


async def backfill_playwright_executions(stats: BackfillStats) -> None:
    object_storage_client = get_object_storage_client()
    async with SessionLocal() as db:
        rows = (
            await db.execute(
                select(PlaywrightToolExecution).where(
                    PlaywrightToolExecution.object_key.is_(None),
                    PlaywrightToolExecution.screenshot_base64.isnot(None),
                    PlaywrightToolExecution.screenshot_base64 != "",
                )
            )
        ).scalars().all()

        for row in rows:
            stats.scanned += 1
            try:
                encoded = (row.screenshot_base64 or "").split(",", 1)[-1]
                payload = base64.b64decode(encoded, validate=False)
                sha256 = hashlib.sha256(payload).hexdigest()
                key = build_playwright_screenshot_key(
                    session_id=str(row.session_id),
                    execution_id=row.execution_id,
                    sha256=sha256,
                    image_format="png",
                )
                stored = await object_storage_client.put_object_bytes(
                    key=key,
                    data=payload,
                    content_type="image/png",
                    metadata={"domain": "playwright", "execution_id": row.execution_id},
                )
                row.object_key = stored.key
                row.object_size = stored.size
                row.object_content_type = stored.content_type
                row.object_etag = stored.etag
                row.storage_provider = stored.provider
                row.storage_bucket = stored.bucket
                row.screenshot_base64 = None
                stats.migrated += 1
            except Exception:
                stats.failed += 1

        await db.commit()


async def backfill_playwright_artifacts(stats: BackfillStats) -> None:
    object_storage_client = get_object_storage_client()
    async with SessionLocal() as db:
        rows = (
            await db.execute(
                select(PlaywrightArtifact).where(
                    PlaywrightArtifact.object_key.is_(None)
                )
            )
        ).scalars().all()

        for row in rows:
            stats.scanned += 1
            try:
                legacy_uri = parse_object_uri(row.file_path)
                if legacy_uri and not row.object_key:
                    bucket, key = legacy_uri
                    row.object_key = key
                    row.storage_bucket = bucket
                    row.storage_provider = "s3"
                    stats.migrated += 1
                    continue

                payload = _load_bytes_from_legacy_file(row.file_path)
                if not payload:
                    stats.skipped += 1
                    continue

                sha256 = hashlib.sha256(payload).hexdigest()
                key = build_storage_key(
                    "playwright",
                    "artifacts",
                    str(row.session_id or "unknown"),
                    str(row.id),
                    filename=row.file_name,
                    sha256=sha256,
                )
                stored = await object_storage_client.put_object_bytes(
                    key=key,
                    data=payload,
                    content_type=row.mime_type or _content_type_from_name(row.file_name),
                    metadata={"domain": "playwright_artifacts", "artifact_id": str(row.id)},
                )
                row.object_key = stored.key
                row.object_size = stored.size
                row.object_content_type = stored.content_type
                row.object_etag = stored.etag
                row.storage_provider = stored.provider
                row.storage_bucket = stored.bucket
                if row.file_path and not row.file_path.startswith("object://"):
                    row.file_path = stored.uri
                stats.migrated += 1
            except Exception:
                stats.failed += 1

        await db.commit()


async def main(report_path: Path) -> dict[str, Any]:
    object_storage_client = get_object_storage_client()
    if not object_storage_client.available:
        raise RuntimeError("Object storage is not configured; cannot run backfill.")

    await object_storage_client.ensure_bucket()

    report = {
        "executed_at": datetime.utcnow().isoformat(),
        "skills": asdict(BackfillStats()),
        "knowledge": asdict(BackfillStats()),
        "playwright_executions": asdict(BackfillStats()),
        "playwright_artifacts": asdict(BackfillStats()),
    }

    skills_stats = BackfillStats()
    await backfill_skills(skills_stats)
    report["skills"] = asdict(skills_stats)

    knowledge_stats = BackfillStats()
    await backfill_knowledge(knowledge_stats)
    report["knowledge"] = asdict(knowledge_stats)

    execution_stats = BackfillStats()
    await backfill_playwright_executions(execution_stats)
    report["playwright_executions"] = asdict(execution_stats)

    artifact_stats = BackfillStats()
    await backfill_playwright_artifacts(artifact_stats)
    report["playwright_artifacts"] = asdict(artifact_stats)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill object storage metadata and payloads.")
    parser.add_argument(
        "--report",
        default=str(BACKEND_DIR / "backfill_object_storage_report.json"),
        help="Path to write the JSON summary report.",
    )
    args = parser.parse_args()
    summary = asyncio.run(main(Path(args.report)))
    print(json.dumps(summary, indent=2))
