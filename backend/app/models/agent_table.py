from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class AgentTable(Base):
    """Custom tables created by agents for structured data storage"""
    __tablename__ = "agent_tables"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Table metadata
    name = Column(String(255), nullable=False)  # Table name (unique per agent)
    display_name = Column(String(255), nullable=False)  # Human-readable name
    description = Column(Text, nullable=True)
    
    # Schema definition (JSON format)
    schema = Column(JSON, nullable=False)  # Column definitions with types, constraints
    
    # Configuration
    is_active = Column(Boolean, default=True)
    max_records = Column(Integer, default=10000)  # Limit records per table
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="tables")
    user = relationship("User")
    records = relationship("AgentTableRecord", back_populates="table", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_agent_table_name', 'agent_id', 'name', unique=True),
        Index('idx_agent_table_user', 'user_id'),
    )


class AgentTableRecord(Base):
    """Individual records stored in agent tables"""
    __tablename__ = "agent_table_records"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("agent_tables.id", ondelete="CASCADE"), nullable=False)
    
    # Record data (JSON format matching table schema)
    data = Column(JSON, nullable=False)
    
    # Metadata
    record_key = Column(String(255), nullable=True)  # Optional unique key for record
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    table = relationship("AgentTable", back_populates="records")
    
    # Indexes
    __table_args__ = (
        Index('idx_table_record', 'table_id', 'record_key'),
        Index('idx_record_created', 'table_id', 'created_at'),
    )
