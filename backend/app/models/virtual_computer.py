from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Index
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from enum import Enum

from app.models.base import BaseModel


class VirtualComputerProvider(str, Enum):
    E2B = "e2b"


class VirtualComputerConfiguration(BaseModel):
    __tablename__ = "virtual_computer_configurations"

    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    enabled = Column(Boolean, default=False)
    provider = Column(String(50), default=VirtualComputerProvider.E2B.value)

    idle_timeout_seconds = Column(Integer, default=300)
    max_runtime_seconds = Column(Integer, default=900)
    memory_mb = Column(Integer, default=512)
    cpu_cores = Column(Float, default=1.0)
    allow_network = Column(Boolean, default=True)

    mcp_enabled = Column(Boolean, default=True)
    mcp_server_ids = Column(JSON, nullable=True)

    agent = relationship("AgentModel", back_populates="virtual_computer_configuration")
    user = relationship("User")

    __table_args__ = (
        Index("idx_virtual_computer_agent", "agent_id"),
        Index("idx_virtual_computer_user", "user_id"),
    )

