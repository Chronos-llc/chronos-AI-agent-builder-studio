from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DependabotAlert(BaseModel):
    __tablename__ = "dependabot_alerts"

    # Alert identification
    github_alert_id = Column(Integer, unique=True, nullable=False, index=True)
    alert_number = Column(Integer, nullable=False)
    node_id = Column(String(100), nullable=False)

    # Package information
    affected_package_name = Column(String(255), nullable=False, index=True)
    affected_range = Column(String(100), nullable=True)
    external_reference = Column(String(500), nullable=True)
    external_identifier = Column(String(100), nullable=True, index=True)
    ghsa_id = Column(String(100), nullable=True, index=True)

    # Severity and state
    severity = Column(String(20), nullable=False, index=True)
    state = Column(String(20), nullable=False, default="open", index=True)
    action = Column(String(20), nullable=False, index=True)

    # Fix information
    fixed_in = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    repository_id = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("github_alert_id", "repository_id", name="uq_alert_repo"),
    )

    def __repr__(self):
        return (
            f"<DependabotAlert(id={self.id}, "
            f"github_alert_id={self.github_alert_id}, "
            f"package={self.affected_package_name}, "
            f"severity={self.severity}, "
            f"state={self.state})>"
        )