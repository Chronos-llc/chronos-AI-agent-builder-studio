from enum import Enum

from sqlalchemy import Boolean, Column, Enum as SQLEnum, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class PhoneNumberProvider(str, Enum):
    TWILIO = "twilio"
    VONAGE = "vonage"


class AgentPhoneNumber(BaseModel):
    __tablename__ = "agent_phone_numbers"

    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(SQLEnum(PhoneNumberProvider), nullable=False, index=True)
    phone_number_e164 = Column(String(32), nullable=False, index=True)
    provider_number_id = Column(String(128), nullable=False, index=True)
    country_code = Column(String(8), nullable=True)
    capabilities = Column(JSON, nullable=False, default=list)
    monthly_cost = Column(Float, nullable=True)
    currency = Column(String(8), nullable=False, default="USD")
    is_selected = Column(Boolean, nullable=False, default=False)
    status = Column(String(32), nullable=False, default="active")
    additional_metadata = Column("metadata", JSON, nullable=True)

    agent = relationship("AgentModel", back_populates="phone_numbers")

    def __repr__(self):
        return f"<AgentPhoneNumber(id={self.id}, provider={self.provider}, number={self.phone_number_e164})>"
