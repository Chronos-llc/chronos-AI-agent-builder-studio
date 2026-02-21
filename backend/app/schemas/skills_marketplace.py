"""Schemas for skills marketplace and moderation workflows."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class SkillMarketplaceListItem(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    version: Optional[str] = None
    is_active: bool
    is_premium: bool
    install_count: int
    download_count: int
    submission_status: str
    visibility: str
    scan_status: str
    scan_confidence: int
    scan_summary: Optional[str] = None
    publisher_username: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillMarketplaceListResponse(BaseModel):
    items: list[SkillMarketplaceListItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class SkillVersionResponse(BaseModel):
    id: int
    skill_id: int
    version: str
    file_name: str
    file_path: str
    file_sha256: str
    is_current: bool
    scan_status: str
    scan_report_json: Optional[dict[str, Any]] = None
    manifest_json: Optional[dict[str, Any]] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillVersionListResponse(BaseModel):
    items: list[SkillVersionResponse]
    total: int


class SkillReviewEventResponse(BaseModel):
    id: int
    skill_id: int
    version_id: Optional[int] = None
    action: str
    actor_user_id: Optional[int] = None
    actor_username: Optional[str] = None
    payload: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class SkillMarketplaceDetailResponse(BaseModel):
    skill: SkillMarketplaceListItem
    current_version: Optional[SkillVersionResponse] = None
    events: list[SkillReviewEventResponse] = []


class SkillFileContentResponse(BaseModel):
    skill_id: int
    version_id: int
    file_name: str
    raw_content: str


class SkillCompareResponse(BaseModel):
    skill_id: int
    base_version_id: int
    head_version_id: int
    diff_text: str
    added_lines: int
    removed_lines: int


class SkillInstallRequest(BaseModel):
    target_type: Literal["agent", "fuzzy"]
    agent_id: Optional[int] = Field(default=None, ge=1)
    version_id: Optional[int] = Field(default=None, ge=1)


class SkillInstallResponse(BaseModel):
    success: bool
    message: str
    target_type: Literal["agent", "fuzzy"]
    target_id: Optional[int] = None
    installation_id: Optional[int] = None


class SkillUploadResponse(BaseModel):
    skill_id: int
    version_id: int
    submission_status: str
    scan_status: str
    scan_confidence: int
    scan_summary: str
    published: bool


class SkillScanResponse(BaseModel):
    skill_id: int
    version_id: Optional[int] = None
    scan_status: str
    scan_confidence: int
    scan_summary: str
    scan_report: dict[str, Any]


class SkillReviewDecisionRequest(BaseModel):
    action: Literal["approve", "reject", "quarantine"]
    notes: Optional[str] = None


class SkillSubmissionDetailResponse(BaseModel):
    submission: SkillMarketplaceListItem
    current_version: Optional[SkillVersionResponse] = None
    events: list[SkillReviewEventResponse] = []


class SkillSubmissionListResponse(BaseModel):
    items: list[SkillMarketplaceListItem]
    total: int
