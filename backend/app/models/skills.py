"""Skills and skills marketplace database models."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

from app.models.base import BaseModel


class SkillSubmissionStatus:
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"
    PUBLISHED = "published"


class SkillVisibility:
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class SkillScanStatus:
    PENDING = "pending"
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    ERROR = "error"


class Skill(BaseModel):
    """Skill model for pre-built agent capabilities and marketplace records."""

    __tablename__ = "agent_skills"

    # Basic information
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True, index=True)
    icon = Column(String(50), nullable=True)

    # File information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    content_preview = Column(Text, nullable=True)

    # Metadata
    is_active = Column(Boolean, server_default="true", nullable=False, index=True)
    is_premium = Column(Boolean, server_default="false", nullable=False)
    install_count = Column(Integer, server_default="0", nullable=False)
    download_count = Column(Integer, server_default="0", nullable=False)

    # Version and parameters
    version = Column(String(20), nullable=True)
    parameters = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)

    # Marketplace lifecycle
    submission_status = Column(
        String(30), nullable=False, index=True, server_default=SkillSubmissionStatus.PUBLISHED
    )
    visibility = Column(String(20), nullable=False, server_default=SkillVisibility.PUBLIC)
    published_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_notes = Column(Text, nullable=True)

    # Security review
    scan_status = Column(String(20), nullable=False, server_default=SkillScanStatus.PENDING)
    scan_confidence = Column(Integer, nullable=False, server_default="0")
    scan_summary = Column(Text, nullable=True)

    # Ownership
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    installations = relationship("AgentSkillInstallation", back_populates="skill", cascade="all, delete-orphan")
    versions = relationship("SkillVersion", back_populates="skill", cascade="all, delete-orphan")
    review_events = relationship("SkillReviewEvent", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.name}', status='{self.submission_status}')>"


class SkillVersion(BaseModel):
    """Immutable skill version record."""

    __tablename__ = "skill_versions"

    skill_id = Column(Integer, ForeignKey("agent_skills.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_sha256 = Column(String(64), nullable=False, index=True)
    raw_content = Column(Text, nullable=True)  # Legacy fallback during object-storage transition.
    object_key = Column(String(1024), nullable=True, index=True)
    object_size = Column(Integer, nullable=True)
    object_content_type = Column(String(255), nullable=True)
    object_etag = Column(String(128), nullable=True)
    storage_provider = Column(String(32), nullable=True)
    storage_bucket = Column(String(128), nullable=True)
    manifest_json = Column(JSON, nullable=True)
    is_current = Column(Boolean, nullable=False, server_default="true")

    scan_status = Column(String(20), nullable=False, server_default=SkillScanStatus.PENDING)
    scan_report_json = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    skill = relationship("Skill", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])
    review_events = relationship("SkillReviewEvent", back_populates="version")

    __table_args__ = (
        UniqueConstraint("skill_id", "version", name="uq_skill_version_per_skill"),
    )

    def __repr__(self):
        return f"<SkillVersion(id={self.id}, skill_id={self.skill_id}, version='{self.version}')>"


class SkillReviewEvent(BaseModel):
    """Moderation event timeline for submitted skills."""

    __tablename__ = "skill_review_events"

    skill_id = Column(Integer, ForeignKey("agent_skills.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("skill_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(40), nullable=False, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    payload = Column(JSON, nullable=False, default=dict)

    skill = relationship("Skill", back_populates="review_events")
    version = relationship("SkillVersion", back_populates="review_events")
    actor = relationship("User", foreign_keys=[actor_user_id])

    def __repr__(self):
        return f"<SkillReviewEvent(id={self.id}, skill_id={self.skill_id}, action='{self.action}')>"


class AgentSkillInstallation(BaseModel):
    """Agent skill installation tracking."""

    __tablename__ = "agent_skill_installations"

    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("agent_skills.id", ondelete="CASCADE"), nullable=False, index=True)
    knowledge_file_id = Column(Integer, ForeignKey("knowledge_files.id", ondelete="SET NULL"), nullable=True)

    configuration = Column(JSON, nullable=True)
    is_enabled = Column(Boolean, server_default="true", nullable=False)
    installed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    agent = relationship("AgentModel", foreign_keys=[agent_id])
    skill = relationship("Skill", back_populates="installations")
    knowledge_file = relationship("KnowledgeFile", foreign_keys=[knowledge_file_id])

    def __repr__(self):
        return f"<AgentSkillInstallation(id={self.id}, agent_id={self.agent_id}, skill_id={self.skill_id})>"
