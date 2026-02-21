from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class IntegrationSubmissionEvent(BaseModel):
    __tablename__ = "integration_submission_events"

    integration_id = Column(Integer, ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(40), nullable=False)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    payload = Column(JSON, nullable=False, default={})

    integration = relationship("Integration", back_populates="submission_events")
    actor = relationship("User")

    def __repr__(self):
        return f"<IntegrationSubmissionEvent(id={self.id}, integration_id={self.integration_id}, action='{self.action}')>"
