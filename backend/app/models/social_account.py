from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SocialAccount(BaseModel):
    __tablename__ = "social_accounts"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(20), nullable=False, index=True)
    provider_user_id = Column(String(255), nullable=False)
    provider_email = Column(String(255), nullable=True)

    user = relationship("User", back_populates="social_accounts")

    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_social_provider_user"),
    )

    def __repr__(self):
        return (
            f"<SocialAccount(id={self.id}, provider='{self.provider}', provider_user_id='{self.provider_user_id}')>"
        )
