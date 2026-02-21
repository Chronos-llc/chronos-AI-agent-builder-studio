"""Dedicated Fuzzy knowledge storage for installed skills."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from app.models.base import BaseModel


class FuzzyKnowledgeEntry(BaseModel):
    __tablename__ = "fuzzy_knowledge_entries"

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    entry_metadata = Column(JSON, nullable=True)
    installed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    installer = relationship("User", foreign_keys=[installed_by])
    skill_installations = relationship(
        "FuzzySkillInstallation", back_populates="knowledge_entry", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<FuzzyKnowledgeEntry(id={self.id}, title='{self.title}')>"


class FuzzySkillInstallation(BaseModel):
    __tablename__ = "fuzzy_skill_installations"

    skill_id = Column(Integer, ForeignKey("agent_skills.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("skill_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    knowledge_entry_id = Column(
        Integer, ForeignKey("fuzzy_knowledge_entries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    installed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(20), nullable=False, server_default="installed")

    skill = relationship("Skill", foreign_keys=[skill_id])
    version = relationship("SkillVersion", foreign_keys=[version_id])
    knowledge_entry = relationship("FuzzyKnowledgeEntry", back_populates="skill_installations")
    installer = relationship("User", foreign_keys=[installed_by])

    def __repr__(self):
        return (
            f"<FuzzySkillInstallation(id={self.id}, skill_id={self.skill_id}, "
            f"knowledge_entry_id={self.knowledge_entry_id})>"
        )
