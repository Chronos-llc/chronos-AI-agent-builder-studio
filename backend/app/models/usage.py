from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
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
    LITE = "lite"
    LOTUS = "lotus"
    TEAM_DEVELOPER = "team_developer"
    SPECIAL_SERVICE = "special_service"
    # Legacy value retained for compatibility while data is migrated.
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ResourceType(enum.Enum):
    AI_SPEND = "ai_spend"
    FILE_STORAGE = "file_storage"
    VECTOR_DB_STORAGE = "vector_db_storage"
    TABLE_ROWS = "table_rows"
    COLLABORATORS = "collaborators"
    AGENTS = "agents"


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
    additional_metadata = Column(String(1000), nullable=True)  # JSON string for additional data
    
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


class WorkspaceMember(BaseModel):
    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "member_user_id", name="uq_workspace_member_owner_member"),
    )

    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    member_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False, default="member")
    status = Column(String(20), nullable=False, default="active", index=True)

    owner = relationship("User", foreign_keys=[owner_user_id], back_populates="workspace_members")
    member = relationship("User", foreign_keys=[member_user_id], back_populates="workspace_memberships")


class UserAddonAllocation(BaseModel):
    __tablename__ = "user_addon_allocations"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_type = Column(Enum(ResourceType), nullable=False, index=True)
    units = Column(Integer, nullable=False, default=1)
    unit_price_usd = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), nullable=False, default="USD")
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    effective_from = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    effective_to = Column(DateTime(timezone=True), nullable=True)
    additional_metadata = Column(JSON, nullable=True)

    user = relationship("User", back_populates="addon_allocations")


class AISpendEvent(BaseModel):
    __tablename__ = "ai_spend_events"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String(100), nullable=True)
    model = Column(String(150), nullable=True)
    cost_amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    tokens = Column(Integer, nullable=True)
    source = Column(String(100), nullable=True)
    additional_metadata = Column(JSON, nullable=True)
    event_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="ai_spend_events")
    agent = relationship("AgentModel", foreign_keys=[agent_id])


class UserBalanceAccount(BaseModel):
    __tablename__ = "user_balance_accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "currency", name="uq_user_balance_account_currency"),
    )

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    currency = Column(String(3), nullable=False, index=True)
    balance = Column(Numeric(precision=16, scale=4), nullable=False, default=0)

    user = relationship("User", back_populates="balance_accounts")


class UserBalanceTransaction(BaseModel):
    __tablename__ = "user_balance_transactions"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    currency = Column(String(3), nullable=False, index=True)
    amount_delta = Column(Numeric(precision=16, scale=4), nullable=False)
    reason = Column(String(255), nullable=False)
    admin_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    additional_metadata = Column(JSON, nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="balance_transactions")
    admin_user = relationship("User", foreign_keys=[admin_user_id])


def can_publish_integration(plan_type: PlanType | None) -> bool:
    if not plan_type:
        return False
    return plan_type in {
        PlanType.TEAM_DEVELOPER,
        PlanType.SPECIAL_SERVICE,
        PlanType.ENTERPRISE,
        PlanType.PRO,  # backward compatibility
    }


def has_team_visibility_access(plan_type: PlanType | None) -> bool:
    if not plan_type:
        return False
    return plan_type in {
        PlanType.TEAM_DEVELOPER,
        PlanType.SPECIAL_SERVICE,
        PlanType.ENTERPRISE,
        PlanType.PRO,  # backward compatibility
    }
