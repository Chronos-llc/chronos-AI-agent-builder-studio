"""Skills marketplace, moderation, scanning, and installation endpoints."""

from __future__ import annotations

import difflib
import hashlib
import io
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.object_storage import (
    ObjectStorageError,
    build_skill_object_key,
    get_object_storage_client,
    make_object_uri,
    parse_object_uri,
)
from app.core.skill_security_scanner import skill_security_scanner
from app.models.admin import AdminUser
from app.models.agent import AgentModel
from app.models.fuzzy_knowledge import FuzzyKnowledgeEntry, FuzzySkillInstallation
from app.models.knowledge import FileType, KnowledgeChunk, KnowledgeFile, KnowledgeFileStatus
from app.models.skills import (
    AgentSkillInstallation,
    Skill,
    SkillReviewEvent,
    SkillScanStatus,
    SkillSubmissionStatus,
    SkillVersion,
    SkillVisibility,
)
from app.models.user import User
from app.schemas.skills_marketplace import (
    SkillCompareResponse,
    SkillFileContentResponse,
    SkillInstallRequest,
    SkillInstallResponse,
    SkillMarketplaceDetailResponse,
    SkillMarketplaceListItem,
    SkillMarketplaceListResponse,
    SkillReviewDecisionRequest,
    SkillReviewEventResponse,
    SkillScanResponse,
    SkillSubmissionDetailResponse,
    SkillSubmissionListResponse,
    SkillUploadResponse,
    SkillVersionListResponse,
    SkillVersionResponse,
)

router = APIRouter()
object_storage_client = get_object_storage_client()

# Allowed base directories for skill file paths (prevents path traversal)
ALLOWED_SKILL_PATHS = [Path("uploads/skills"), Path("backend/uploads/skills")]


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\-_\s]", "", value).strip().lower()
    cleaned = re.sub(r"[\s_]+", "-", cleaned)
    return cleaned[:96]


def _parse_frontmatter(markdown_content: str) -> tuple[dict[str, str], str]:
    content = markdown_content.lstrip("\ufeff")
    if not content.startswith("---\n"):
        return {}, markdown_content

    lines = content.splitlines()
    if not lines:
        return {}, markdown_content

    end_index: Optional[int] = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break

    if end_index is None:
        return {}, markdown_content

    frontmatter_lines = lines[1:end_index]
    body = "\n".join(lines[end_index + 1 :]).strip()

    parsed: dict[str, str] = {}
    for raw_line in frontmatter_lines:
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip().lower()
        value = raw_value.strip().strip('"').strip("'")
        if key:
            parsed[key] = value

    return parsed, body


def _split_tags(tags_csv: Optional[str]) -> list[str]:
    if not tags_csv:
        return []
    return [tag.strip() for tag in tags_csv.split(",") if tag.strip()]


def _build_manifest(skill: Skill, version: SkillVersion) -> dict[str, Any]:
    return {
        "skill_id": skill.id,
        "name": skill.name,
        "display_name": skill.display_name,
        "description": skill.description,
        "category": skill.category,
        "version": version.version,
        "file_name": version.file_name,
        "file_sha256": version.file_sha256,
        "object_key": version.object_key,
        "storage_bucket": version.storage_bucket,
        "published_at": skill.published_at.isoformat() if skill.published_at else None,
        "scan_status": version.scan_status,
        "scan_summary": skill.scan_summary,
        "created_at": version.created_at.isoformat(),
    }


def _chunk_text(content: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    if not content:
        return []
    chunks: list[str] = []
    start = 0
    length = len(content)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(content[start:end])
        if end >= length:
            break
        start = max(0, end - overlap)
    return chunks


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()


async def _is_admin(user: User, db: AsyncSession) -> bool:
    if user.is_superuser:
        return True
    result = await db.execute(
        select(AdminUser).where(
            and_(AdminUser.user_id == user.id, AdminUser.is_active == True)
        )
    )
    return result.scalar_one_or_none() is not None


async def _require_admin(user: User, db: AsyncSession) -> None:
    if not await _is_admin(user, db):
        raise HTTPException(status_code=403, detail="Admin access required")


def _validate_visibility(value: str) -> str:
    if value not in {SkillVisibility.PUBLIC, SkillVisibility.PRIVATE, SkillVisibility.UNLISTED}:
        raise HTTPException(status_code=400, detail="Invalid visibility value")
    return value


async def _get_current_version(db: AsyncSession, skill_id: int) -> SkillVersion | None:
    result = await db.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_id == skill_id)
        .order_by(desc(SkillVersion.is_current), desc(SkillVersion.created_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


def _skill_to_item(skill: Skill) -> SkillMarketplaceListItem:
    return SkillMarketplaceListItem(
        id=skill.id,
        name=skill.name,
        display_name=skill.display_name,
        description=skill.description,
        category=skill.category,
        icon=skill.icon,
        version=skill.version,
        is_active=bool(skill.is_active),
        is_premium=bool(skill.is_premium),
        install_count=int(skill.install_count or 0),
        download_count=int(skill.download_count or 0),
        submission_status=skill.submission_status,
        visibility=skill.visibility,
        scan_status=skill.scan_status,
        scan_confidence=int(skill.scan_confidence or 0),
        scan_summary=skill.scan_summary,
        publisher_username=skill.creator.username if skill.creator else None,
        published_at=skill.published_at,
        created_at=skill.created_at,
        updated_at=skill.updated_at,
    )


def _event_to_schema(event: SkillReviewEvent) -> SkillReviewEventResponse:
    return SkillReviewEventResponse(
        id=event.id,
        skill_id=event.skill_id,
        version_id=event.version_id,
        action=event.action,
        actor_user_id=event.actor_user_id,
        actor_username=event.actor.username if event.actor else None,
        payload=event.payload or {},
        created_at=event.created_at,
    )


async def _append_review_event(
    db: AsyncSession,
    skill_id: int,
    action: str,
    actor_user_id: Optional[int],
    version_id: Optional[int] = None,
    payload: Optional[dict[str, Any]] = None,
) -> SkillReviewEvent:
    event = SkillReviewEvent(
        skill_id=skill_id,
        version_id=version_id,
        action=action,
        actor_user_id=actor_user_id,
        payload=payload or {},
    )
    db.add(event)
    await db.flush()
    return event


async def _resolve_visible_skill(skill: Skill, current_user: User, db: AsyncSession) -> Skill:
    admin_access = await _is_admin(current_user, db)
    if admin_access:
        return skill

    is_owner = skill.created_by == current_user.id
    is_publicly_listed = (
        skill.submission_status == SkillSubmissionStatus.PUBLISHED
        and skill.visibility == SkillVisibility.PUBLIC
    )
    if not is_owner and not is_publicly_listed:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


async def _load_skill_version_bytes(version: SkillVersion) -> bytes:
    if version.object_key:
        try:
            return await object_storage_client.get_object_bytes(version.object_key)
        except ObjectStorageError:
            # Fall back to legacy fields during transition.
            pass

    if version.raw_content is not None:
        return version.raw_content.encode("utf-8", errors="ignore")

    object_uri = parse_object_uri(version.file_path)
    if object_uri:
        _, key = object_uri
        try:
            return await object_storage_client.get_object_bytes(key)
        except ObjectStorageError:
            pass

    if version.file_path and Path(version.file_path).exists():
        resolved_path = Path(version.file_path).resolve()
        # Validate path is within allowed directories to prevent path traversal
        is_allowed = any(
            str(resolved_path).startswith(str(allowed.resolve()))
            for allowed in ALLOWED_SKILL_PATHS
            if allowed.exists()
        )
        if not is_allowed:
            raise HTTPException(status_code=400, detail="Invalid file path")
        return resolved_path.read_bytes()

    raise HTTPException(status_code=404, detail="Skill file content is unavailable")


async def _load_skill_version_text(version: SkillVersion) -> str:
    payload = await _load_skill_version_bytes(version)
    return payload.decode("utf-8", errors="replace")


@router.get("/marketplace", response_model=SkillMarketplaceListResponse)
async def list_marketplace_skills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search_query: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    admin_access = await _is_admin(current_user, db)

    query = select(Skill).options(joinedload(Skill.creator))
    if not admin_access:
        query = query.where(
            or_(
                and_(
                    Skill.submission_status == SkillSubmissionStatus.PUBLISHED,
                    Skill.visibility == SkillVisibility.PUBLIC,
                ),
                Skill.created_by == current_user.id,
            )
        )

    if search_query:
        pattern = f"%{search_query}%"
        query = query.where(
            or_(
                Skill.name.ilike(pattern),
                Skill.display_name.ilike(pattern),
                Skill.description.ilike(pattern),
            )
        )

    if category:
        query = query.where(Skill.category == category)

    sort_field = Skill.created_at
    if sort_by == "install_count":
        sort_field = Skill.install_count
    elif sort_by == "download_count":
        sort_field = Skill.download_count
    elif sort_by == "name":
        sort_field = Skill.name

    query = query.order_by(sort_field.asc() if sort_order == "asc" else sort_field.desc())

    total_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_query)).scalar_one()

    query = query.offset((page - 1) * page_size).limit(page_size)
    skills = (await db.execute(query)).scalars().all()

    return SkillMarketplaceListResponse(
        items=[_skill_to_item(skill) for skill in skills],
        total=total,
        page=page,
        page_size=page_size,
        has_more=page * page_size < total,
    )


@router.get("/marketplace/{skill_id}", response_model=SkillMarketplaceDetailResponse)
async def get_marketplace_skill_detail(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skill = (
        await db.execute(
            select(Skill).options(joinedload(Skill.creator)).where(Skill.id == skill_id)
        )
    ).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill = await _resolve_visible_skill(skill, current_user, db)

    version = await _get_current_version(db, skill.id)
    events = (
        await db.execute(
            select(SkillReviewEvent)
            .options(joinedload(SkillReviewEvent.actor))
            .where(SkillReviewEvent.skill_id == skill.id)
            .order_by(desc(SkillReviewEvent.created_at))
            .limit(30)
        )
    ).scalars().all()

    return SkillMarketplaceDetailResponse(
        skill=_skill_to_item(skill),
        current_version=SkillVersionResponse.model_validate(version) if version else None,
        events=[_event_to_schema(event) for event in events],
    )


@router.get("/marketplace/{skill_id}/versions", response_model=SkillVersionListResponse)
async def list_skill_versions(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skill = (
        await db.execute(
            select(Skill).options(joinedload(Skill.creator)).where(Skill.id == skill_id)
        )
    ).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await _resolve_visible_skill(skill, current_user, db)

    versions = (
        await db.execute(
            select(SkillVersion)
            .where(SkillVersion.skill_id == skill_id)
            .order_by(desc(SkillVersion.created_at))
        )
    ).scalars().all()
    return SkillVersionListResponse(
        items=[SkillVersionResponse.model_validate(version) for version in versions],
        total=len(versions),
    )


@router.get("/marketplace/{skill_id}/versions/{version_id}/file", response_model=SkillFileContentResponse)
async def get_skill_version_file(
    skill_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skill = (
        await db.execute(
            select(Skill).options(joinedload(Skill.creator)).where(Skill.id == skill_id)
        )
    ).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await _resolve_visible_skill(skill, current_user, db)

    version = (
        await db.execute(
            select(SkillVersion).where(
                and_(SkillVersion.id == version_id, SkillVersion.skill_id == skill_id)
            )
        )
    ).scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Skill version not found")

    raw_content = await _load_skill_version_text(version)

    return SkillFileContentResponse(
        skill_id=skill_id,
        version_id=version_id,
        file_name=version.file_name,
        raw_content=raw_content,
    )


@router.get("/marketplace/{skill_id}/compare", response_model=SkillCompareResponse)
async def compare_skill_versions(
    skill_id: int,
    base_version_id: int = Query(...),
    head_version_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skill = (
        await db.execute(
            select(Skill).options(joinedload(Skill.creator)).where(Skill.id == skill_id)
        )
    ).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await _resolve_visible_skill(skill, current_user, db)

    versions = (
        await db.execute(
            select(SkillVersion).where(
                and_(
                    SkillVersion.skill_id == skill_id,
                    SkillVersion.id.in_([base_version_id, head_version_id]),
                )
            )
        )
    ).scalars().all()
    version_map = {version.id: version for version in versions}
    base_version = version_map.get(base_version_id)
    head_version = version_map.get(head_version_id)
    if not base_version or not head_version:
        raise HTTPException(status_code=404, detail="One or both versions were not found")

    base_content = await _load_skill_version_text(base_version)
    head_content = await _load_skill_version_text(head_version)

    base_lines = base_content.splitlines(keepends=True)
    head_lines = head_content.splitlines(keepends=True)
    diff_lines = list(
        difflib.unified_diff(
            base_lines,
            head_lines,
            fromfile=f"{base_version.file_name}@{base_version.version}",
            tofile=f"{head_version.file_name}@{head_version.version}",
            lineterm="",
        )
    )
    added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))

    return SkillCompareResponse(
        skill_id=skill_id,
        base_version_id=base_version_id,
        head_version_id=head_version_id,
        diff_text="\n".join(diff_lines),
        added_lines=added,
        removed_lines=removed,
    )


@router.post("/marketplace/upload", response_model=SkillUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_marketplace_skill(
    skill_file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    display_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    icon: Optional[str] = Form(None),
    version: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    is_premium: bool = Form(False),
    visibility: str = Form(SkillVisibility.PUBLIC),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    filename = skill_file.filename or "SKILL.md"
    if not filename.lower().endswith(".md"):
        raise HTTPException(status_code=400, detail="Only SKILL.md markdown files are supported")

    raw_bytes = await skill_file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(raw_bytes) > settings.UPLOAD_MAX_SIZE:
        raise HTTPException(status_code=413, detail="Skill file exceeds maximum upload size")

    raw_content = raw_bytes.decode("utf-8", errors="replace")
    frontmatter, _body = _parse_frontmatter(raw_content)
    admin_access = await _is_admin(current_user, db)
    visibility = _validate_visibility(visibility)

    parsed_name = name or frontmatter.get("name") or Path(filename).stem
    skill_name = _slugify(parsed_name)
    if not skill_name:
        raise HTTPException(status_code=400, detail="Unable to infer a valid skill name")

    parsed_display_name = display_name or frontmatter.get("display_name") or skill_name.replace("-", " ").title()
    parsed_description = description or frontmatter.get("description") or "No description provided."
    version_label = version or frontmatter.get("version") or "1.0.0"
    tag_list = _split_tags(tags) if tags else []

    existing_skill = (
        await db.execute(select(Skill).where(Skill.name == skill_name))
    ).scalar_one_or_none()

    if existing_skill and existing_skill.created_by not in {None, current_user.id} and not admin_access:
        raise HTTPException(
            status_code=400,
            detail="A skill with this name already exists and belongs to another publisher",
        )

    if not existing_skill:
        skill = Skill(
            name=skill_name,
            display_name=parsed_display_name,
            description=parsed_description,
            category=category,
            icon=icon,
            version=version_label,
            file_path="pending",
            file_size=len(raw_bytes),
            content_preview=raw_content[:700],
            is_active=False,
            is_premium=is_premium,
            tags=tag_list,
            created_by=current_user.id,
            visibility=visibility,
            submission_status=SkillSubmissionStatus.DRAFT,
            scan_status=SkillScanStatus.PENDING,
            scan_confidence=0,
        )
        db.add(skill)
        await db.flush()
    else:
        skill = existing_skill
        skill.display_name = parsed_display_name
        skill.description = parsed_description
        skill.category = category or skill.category
        skill.icon = icon or skill.icon
        skill.is_premium = is_premium
        skill.visibility = visibility
        skill.file_size = len(raw_bytes)
        skill.content_preview = raw_content[:700]
        skill.tags = tag_list or skill.tags

    version_exists = (
        await db.execute(
            select(SkillVersion).where(
                and_(SkillVersion.skill_id == skill.id, SkillVersion.version == version_label)
            )
        )
    ).scalar_one_or_none()
    if version_exists:
        version_label = f"{version_label}-{int(datetime.utcnow().timestamp())}"

    file_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    object_key = build_skill_object_key(
        skill_id=skill.id,
        version=version_label,
        sha256=file_sha256,
        filename=filename,
    )
    content_type = skill_file.content_type or "text/markdown"
    try:
        stored_object = await object_storage_client.put_object_bytes(
            key=object_key,
            data=raw_bytes,
            content_type=content_type,
            metadata={
                "skill_name": skill_name,
                "version": version_label,
            },
        )
    except ObjectStorageError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Object storage unavailable for skill upload: {exc}",
        ) from exc

    scan = await skill_security_scanner.scan_skill(filename=filename, raw_content=raw_content)
    scan_dict = scan.to_dict()
    scan_status = scan.status

    if admin_access:
        if scan_status == SkillScanStatus.BENIGN:
            submission_status = SkillSubmissionStatus.PUBLISHED
        elif scan_status == SkillScanStatus.MALICIOUS:
            submission_status = SkillSubmissionStatus.QUARANTINED
        else:
            submission_status = SkillSubmissionStatus.UNDER_REVIEW
    else:
        if scan_status == SkillScanStatus.MALICIOUS:
            submission_status = SkillSubmissionStatus.QUARANTINED
        else:
            submission_status = SkillSubmissionStatus.PENDING_REVIEW

    if not admin_access and submission_status != SkillSubmissionStatus.PUBLISHED:
        skill.visibility = SkillVisibility.PRIVATE

    existing_versions = (
        await db.execute(select(SkillVersion).where(SkillVersion.skill_id == skill.id))
    ).scalars().all()
    for item in existing_versions:
        item.is_current = False

    version_record = SkillVersion(
        skill_id=skill.id,
        version=version_label,
        file_name=filename,
        file_path=stored_object.uri,
        file_sha256=file_sha256,
        raw_content="",
        object_key=stored_object.key,
        object_size=stored_object.size,
        object_content_type=stored_object.content_type,
        object_etag=stored_object.etag,
        storage_provider=stored_object.provider,
        storage_bucket=stored_object.bucket,
        manifest_json={},
        is_current=True,
        scan_status=scan_status,
        scan_report_json=scan_dict["report"],
        created_by=current_user.id,
    )
    db.add(version_record)
    await db.flush()

    manifest = _build_manifest(skill, version_record)
    version_record.manifest_json = manifest

    skill.file_path = stored_object.uri
    skill.version = version_label
    skill.scan_status = scan_status
    skill.scan_confidence = scan.confidence
    skill.scan_summary = scan.summary
    skill.submission_status = submission_status
    skill.is_active = submission_status == SkillSubmissionStatus.PUBLISHED
    if submission_status == SkillSubmissionStatus.PUBLISHED:
        skill.published_at = datetime.utcnow()

    await _append_review_event(
        db=db,
        skill_id=skill.id,
        version_id=version_record.id,
        action="uploaded",
        actor_user_id=current_user.id,
        payload={
            "submission_status": submission_status,
            "scan_status": scan_status,
            "scan_confidence": scan.confidence,
        },
    )

    if submission_status == SkillSubmissionStatus.PUBLISHED and admin_access:
        await _append_review_event(
            db=db,
            skill_id=skill.id,
            version_id=version_record.id,
            action="auto_published",
            actor_user_id=current_user.id,
            payload={"reason": "admin_upload_benign"},
        )

    await db.commit()
    await db.refresh(skill)
    await db.refresh(version_record)

    return SkillUploadResponse(
        skill_id=skill.id,
        version_id=version_record.id,
        submission_status=skill.submission_status,
        scan_status=skill.scan_status,
        scan_confidence=skill.scan_confidence,
        scan_summary=skill.scan_summary or "",
        published=skill.submission_status == SkillSubmissionStatus.PUBLISHED,
    )


@router.get("/marketplace/{skill_id}/download")
async def download_skill_zip(
    skill_id: int,
    version_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skill = (
        await db.execute(
            select(Skill).options(joinedload(Skill.creator)).where(Skill.id == skill_id)
        )
    ).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill = await _resolve_visible_skill(skill, current_user, db)

    if version_id:
        version = (
            await db.execute(
                select(SkillVersion).where(
                    and_(SkillVersion.id == version_id, SkillVersion.skill_id == skill.id)
                )
            )
        ).scalar_one_or_none()
    else:
        version = await _get_current_version(db, skill.id)
    if not version:
        raise HTTPException(status_code=404, detail="Skill version not found")

    version_content = await _load_skill_version_text(version)
    manifest = version.manifest_json or _build_manifest(skill, version)
    readme = (
        f"# {skill.display_name}\n\n"
        f"{skill.description or 'No description provided.'}\n\n"
        f"Publisher: {(skill.creator.username if skill.creator else 'unknown')}\n"
        f"Version: {version.version}\n"
    )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SKILL.md", version_content)
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.writestr("README.txt", readme)

    buffer.seek(0)
    skill.download_count = int(skill.download_count or 0) + 1
    await db.commit()

    archive_name = f"{skill.name}-{version.version}.zip"
    headers = {"Content-Disposition": f'attachment; filename="{archive_name}"'}
    return StreamingResponse(buffer, media_type="application/zip", headers=headers)


async def _load_skill_for_admin_queue(db: AsyncSession, skill_id: int) -> Skill:
    skill = (
        await db.execute(
            select(Skill).options(joinedload(Skill.creator)).where(Skill.id == skill_id)
        )
    ).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


async def _resolve_version_for_skill(
    db: AsyncSession,
    skill_id: int,
    version_id: Optional[int],
) -> SkillVersion:
    version: SkillVersion | None
    if version_id is None:
        version = await _get_current_version(db, skill_id)
    else:
        version = (
            await db.execute(
                select(SkillVersion).where(
                    and_(SkillVersion.skill_id == skill_id, SkillVersion.id == version_id)
                )
            )
        ).scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Skill version not found")
    return version


def _publish_allowed(skill: Skill) -> bool:
    return skill.scan_status in {
        SkillScanStatus.BENIGN,
        SkillScanStatus.SUSPICIOUS,
    } and skill.submission_status in {
        SkillSubmissionStatus.APPROVED,
        SkillSubmissionStatus.UNDER_REVIEW,
        SkillSubmissionStatus.PENDING_REVIEW,
    }


@router.get("/admin/submissions", response_model=SkillSubmissionListResponse)
async def list_skill_submissions(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(current_user, db)

    query = (
        select(Skill)
        .options(joinedload(Skill.creator))
        .where(Skill.submission_status != SkillSubmissionStatus.DRAFT)
        .order_by(desc(Skill.updated_at))
    )

    if status_filter:
        query = query.where(Skill.submission_status == status_filter)
    else:
        query = query.where(
            Skill.submission_status.in_(
                [
                    SkillSubmissionStatus.PENDING_REVIEW,
                    SkillSubmissionStatus.UNDER_REVIEW,
                    SkillSubmissionStatus.APPROVED,
                    SkillSubmissionStatus.REJECTED,
                    SkillSubmissionStatus.QUARANTINED,
                ]
            )
        )

    skills = (await db.execute(query)).scalars().all()
    return SkillSubmissionListResponse(
        items=[_skill_to_item(skill) for skill in skills],
        total=len(skills),
    )


@router.get("/admin/submissions/{skill_id}", response_model=SkillSubmissionDetailResponse)
async def get_submission_detail(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(current_user, db)
    skill = await _load_skill_for_admin_queue(db, skill_id)
    version = await _get_current_version(db, skill.id)
    events = (
        await db.execute(
            select(SkillReviewEvent)
            .options(joinedload(SkillReviewEvent.actor))
            .where(SkillReviewEvent.skill_id == skill.id)
            .order_by(desc(SkillReviewEvent.created_at))
            .limit(50)
        )
    ).scalars().all()

    return SkillSubmissionDetailResponse(
        submission=_skill_to_item(skill),
        current_version=SkillVersionResponse.model_validate(version) if version else None,
        events=[_event_to_schema(event) for event in events],
    )


@router.post("/admin/submissions/{skill_id}/scan", response_model=SkillScanResponse)
async def scan_submission(
    skill_id: int,
    version_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(current_user, db)
    skill = await _load_skill_for_admin_queue(db, skill_id)
    version = await _resolve_version_for_skill(db, skill.id, version_id)
    version_content = await _load_skill_version_text(version)

    scan = await skill_security_scanner.scan_skill(
        filename=version.file_name,
        raw_content=version_content,
    )
    scan_payload = scan.to_dict()
    scan_report = scan_payload["report"]

    version.scan_status = scan.status
    version.scan_report_json = scan_report
    skill.scan_status = scan.status
    skill.scan_confidence = scan.confidence
    skill.scan_summary = scan.summary
    if scan.status == SkillScanStatus.MALICIOUS:
        skill.submission_status = SkillSubmissionStatus.QUARANTINED
        skill.is_active = False
    elif skill.submission_status in {
        SkillSubmissionStatus.PENDING_REVIEW,
        SkillSubmissionStatus.DRAFT,
    }:
        skill.submission_status = SkillSubmissionStatus.UNDER_REVIEW

    await _append_review_event(
        db=db,
        skill_id=skill.id,
        version_id=version.id,
        action="scan_rerun",
        actor_user_id=current_user.id,
        payload={
            "scan_status": scan.status,
            "scan_confidence": scan.confidence,
            "scan_summary": scan.summary,
        },
    )

    await db.commit()

    return SkillScanResponse(
        skill_id=skill.id,
        version_id=version.id,
        scan_status=scan.status,
        scan_confidence=scan.confidence,
        scan_summary=scan.summary,
        scan_report=scan_report,
    )


@router.post("/admin/submissions/{skill_id}/review", response_model=SkillSubmissionDetailResponse)
async def review_submission(
    skill_id: int,
    review: SkillReviewDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(current_user, db)
    skill = await _load_skill_for_admin_queue(db, skill_id)
    version = await _get_current_version(db, skill.id)
    if not version:
        raise HTTPException(status_code=404, detail="No version found for this skill")

    if review.action == "approve":
        if skill.scan_status == SkillScanStatus.MALICIOUS:
            raise HTTPException(status_code=400, detail="Malicious submissions cannot be approved")
        skill.submission_status = SkillSubmissionStatus.APPROVED
    elif review.action == "reject":
        skill.submission_status = SkillSubmissionStatus.REJECTED
        skill.is_active = False
    else:
        skill.submission_status = SkillSubmissionStatus.QUARANTINED
        skill.is_active = False

    skill.reviewed_at = datetime.utcnow()
    skill.reviewed_by = current_user.id
    skill.review_notes = review.notes

    await _append_review_event(
        db=db,
        skill_id=skill.id,
        version_id=version.id,
        action=f"review_{review.action}",
        actor_user_id=current_user.id,
        payload={"notes": review.notes},
    )

    await db.commit()
    await db.refresh(skill)

    events = (
        await db.execute(
            select(SkillReviewEvent)
            .options(joinedload(SkillReviewEvent.actor))
            .where(SkillReviewEvent.skill_id == skill.id)
            .order_by(desc(SkillReviewEvent.created_at))
            .limit(50)
        )
    ).scalars().all()

    return SkillSubmissionDetailResponse(
        submission=_skill_to_item(skill),
        current_version=SkillVersionResponse.model_validate(version),
        events=[_event_to_schema(event) for event in events],
    )


@router.post("/admin/submissions/{skill_id}/publish", response_model=SkillSubmissionDetailResponse)
async def publish_submission(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(current_user, db)
    skill = await _load_skill_for_admin_queue(db, skill_id)
    version = await _get_current_version(db, skill.id)
    if not version:
        raise HTTPException(status_code=404, detail="No version found for this skill")

    if not _publish_allowed(skill):
        raise HTTPException(
            status_code=400,
            detail=(
                "Submission must be approved (or under review) with benign/suspicious scan "
                "before publishing"
            ),
        )
    if skill.scan_status == SkillScanStatus.MALICIOUS:
        raise HTTPException(status_code=400, detail="Malicious skills cannot be published")

    skill.submission_status = SkillSubmissionStatus.PUBLISHED
    skill.published_at = datetime.utcnow()
    skill.reviewed_at = datetime.utcnow()
    skill.reviewed_by = current_user.id
    skill.is_active = True
    if skill.visibility == SkillVisibility.PRIVATE:
        skill.visibility = SkillVisibility.PUBLIC

    await _append_review_event(
        db=db,
        skill_id=skill.id,
        version_id=version.id,
        action="published",
        actor_user_id=current_user.id,
        payload={"scan_status": skill.scan_status},
    )

    await db.commit()
    await db.refresh(skill)

    events = (
        await db.execute(
            select(SkillReviewEvent)
            .options(joinedload(SkillReviewEvent.actor))
            .where(SkillReviewEvent.skill_id == skill.id)
            .order_by(desc(SkillReviewEvent.created_at))
            .limit(50)
        )
    ).scalars().all()

    return SkillSubmissionDetailResponse(
        submission=_skill_to_item(skill),
        current_version=SkillVersionResponse.model_validate(version),
        events=[_event_to_schema(event) for event in events],
    )


@router.post("/marketplace/{skill_id}/install", response_model=SkillInstallResponse)
async def install_skill(
    skill_id: int,
    payload: SkillInstallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skill = (
        await db.execute(
            select(Skill).options(joinedload(Skill.creator)).where(Skill.id == skill_id)
        )
    ).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill = await _resolve_visible_skill(skill, current_user, db)
    if skill.submission_status != SkillSubmissionStatus.PUBLISHED:
        admin_access = await _is_admin(current_user, db)
        if not admin_access and skill.created_by != current_user.id:
            raise HTTPException(status_code=400, detail="Skill is not published yet")

    version = await _resolve_version_for_skill(db, skill.id, payload.version_id)
    version_content = await _load_skill_version_text(version)
    version_bytes = version_content.encode("utf-8", errors="ignore")

    if payload.target_type == "agent":
        if not payload.agent_id:
            raise HTTPException(status_code=400, detail="agent_id is required for agent installs")

        agent = (
            await db.execute(select(AgentModel).where(AgentModel.id == payload.agent_id))
        ).scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Target agent not found")

        admin_access = await _is_admin(current_user, db)
        if agent.owner_id != current_user.id and not admin_access:
            raise HTTPException(status_code=403, detail="Not authorized to install on this agent")

        stored_filename = f"skill-{skill.id}-{version.id}-{int(datetime.utcnow().timestamp())}.md"
        knowledge_file = KnowledgeFile(
            original_filename=version.file_name,
            stored_filename=stored_filename,
            file_path=version.file_path,
            object_key=version.object_key,
            object_size=version.object_size or len(version_bytes),
            object_content_type=version.object_content_type or "text/markdown",
            object_etag=version.object_etag,
            storage_provider=version.storage_provider,
            storage_bucket=version.storage_bucket,
            file_type=FileType.TEXT,
            file_size=len(version_bytes),
            mime_type="text/markdown",
            content_text=version_content,
            content_summary=(skill.description or "")[:500] or None,
            processing_status=KnowledgeFileStatus.READY,
            additional_metadata={
                "source": "skill_marketplace",
                "skill_id": skill.id,
                "skill_name": skill.name,
                "version_id": version.id,
                "version": version.version,
            },
            tags=skill.tags or [],
            agent_id=agent.id,
        )
        db.add(knowledge_file)
        await db.flush()

        chunks = _chunk_text(version_content)
        for idx, chunk_content in enumerate(chunks):
            db.add(
                KnowledgeChunk(
                    knowledge_file_id=knowledge_file.id,
                    chunk_index=idx,
                    content=chunk_content,
                    content_hash=_content_hash(chunk_content),
                    chunk_metadata={
                        "source": "skill",
                        "skill_id": skill.id,
                        "version_id": version.id,
                    },
                )
            )

        installation = (
            await db.execute(
                select(AgentSkillInstallation).where(
                    and_(
                        AgentSkillInstallation.agent_id == agent.id,
                        AgentSkillInstallation.skill_id == skill.id,
                    )
                )
            )
        ).scalar_one_or_none()

        if installation:
            installation.knowledge_file_id = knowledge_file.id
            configuration = dict(installation.configuration or {})
            configuration.update(
                {
                    "version_id": version.id,
                    "version": version.version,
                    "installed_at": datetime.utcnow().isoformat(),
                }
            )
            installation.configuration = configuration
            installation.is_enabled = True
        else:
            installation = AgentSkillInstallation(
                agent_id=agent.id,
                skill_id=skill.id,
                knowledge_file_id=knowledge_file.id,
                configuration={
                    "version_id": version.id,
                    "version": version.version,
                    "installed_at": datetime.utcnow().isoformat(),
                },
                is_enabled=True,
            )
            db.add(installation)

        skill.install_count = int(skill.install_count or 0) + 1
        await _append_review_event(
            db=db,
            skill_id=skill.id,
            version_id=version.id,
            action="installed_agent",
            actor_user_id=current_user.id,
            payload={"agent_id": agent.id, "knowledge_file_id": knowledge_file.id},
        )
        await db.commit()
        await db.refresh(installation)

        return SkillInstallResponse(
            success=True,
            message="Skill installed to agent knowledge base",
            target_type="agent",
            target_id=agent.id,
            installation_id=installation.id,
        )

    admin_access = await _is_admin(current_user, db)
    if not admin_access:
        raise HTTPException(status_code=403, detail="Fuzzy installs require admin access")

    knowledge_entry = FuzzyKnowledgeEntry(
        title=f"{skill.display_name} ({version.version})",
        content=version_content,
        content_hash=_content_hash(version_content),
        entry_metadata={
            "source": "skill_marketplace",
            "skill_id": skill.id,
            "skill_name": skill.name,
            "version_id": version.id,
            "version": version.version,
            "publisher_username": skill.creator.username if skill.creator else None,
        },
        installed_by=current_user.id,
    )
    db.add(knowledge_entry)
    await db.flush()

    fuzzy_installation = FuzzySkillInstallation(
        skill_id=skill.id,
        version_id=version.id,
        knowledge_entry_id=knowledge_entry.id,
        installed_by=current_user.id,
        status="installed",
    )
    db.add(fuzzy_installation)
    skill.install_count = int(skill.install_count or 0) + 1

    await _append_review_event(
        db=db,
        skill_id=skill.id,
        version_id=version.id,
        action="installed_fuzzy",
        actor_user_id=current_user.id,
        payload={"knowledge_entry_id": knowledge_entry.id},
    )

    await db.commit()
    await db.refresh(fuzzy_installation)

    return SkillInstallResponse(
        success=True,
        message="Skill installed to Fuzzy knowledge base",
        target_type="fuzzy",
        target_id=knowledge_entry.id,
        installation_id=fuzzy_installation.id,
    )
