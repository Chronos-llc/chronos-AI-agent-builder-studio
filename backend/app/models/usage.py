from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import BaseModel


class UsageType(enum.Enum):
    API_CALL = "api_call"
    STORAGE = "storage"
    AGENT_CREATION = "agent_creation"
    FILE_UPLOAD = "file_upload"


class PlanType(enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UsageRecord(BaseModel):
    __tablename__ = "usage_records"
    
    # Usage information
    usage_type = Column(Enum(UsageType), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)  # Amount used
    unit = Column(String(50), nullable=False)  # calls, bytes, agents, etc.
    
    # Context
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    metadata = Column(String(1000), nullable=True)  # JSON string for additional data
    
    # Relationships
    agent = relationship("AgentModel", back_populates="usage_records")
    user = relationship("User", back_populates="usage_records")
    
    def __repr__(self):
        return f"<UsageRecord(id={self.id}, type='{self.usage_type}', amount={self.amount}, user_id={self.user_id})>"


class UserPlan(BaseModel):
    __tablename__ = "user_plans"
    
    # Plan information
    plan_type = Column(Enum(PlanType), nullable=False, default=PlanType.FREE)
    is_active = Column(Boolean, default=True)
    
    # Limits
    max_agents = Column(Integer, nullable=False, default=5)
    max_api_calls_monthly = Column(Integer, nullable=False, default=1000)
    max_storage_mb = Column(Integer, nullable=False, default=100)
    
    # Current usage
    current_agents = Column(Integer, nullable=False, default=0)
    current_api_calls_month = Column(Integer, nullable=False, default=0)
    current_storage_mb = Column(Integer, nullable=False, default=0)
    
    # Billing
    billing_cycle_start = Column(DateTime, nullable=True)
    billing_cycle_end = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Relationships
    user = relationship("User", back_populates="plan")
    
    def __repr__(self):
        return f"<UserPlan(user_id={self.user_id}, plan='{self.plan_type}', active={self.is_active})>"

    def can_create_agent(self) -> bool:
        return self.current_agents < self.max_agents

    def can_make_api_call(self) -> bool:
        return self.current_api_calls_month < self.max_api_calls_monthly

    def can_use_storage(self, additional_mb: float) -> bool:
        return (self.current_storage_mb + additional_mb) <= self.max_storage_mb

    def get_usage_percentage(self) -> dict:
        return {
            "agents": (self.current_agents / self.max_agents) * 100,
            "api_calls": (self.current_api_calls_month / self.max_api_calls_monthly) * 100,
            "storage": (self.current_storage_mb / self.max_storage_mb) * 100
        }