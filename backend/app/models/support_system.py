from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.models.base import BaseModel
from app.models.user import User


class SupportMessage(BaseModel):
    """Support ticket/messaging system"""
    __tablename__ = "support_messages"
    
    # Basic information
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), server_default='OPEN', nullable=False)  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(20), server_default='NORMAL', nullable=False)  # LOW, NORMAL, HIGH, CRITICAL
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(50), nullable=True)  # e.g., BUG, FEATURE_REQUEST, BILLING, TECHNICAL
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assigned_admin = relationship("User", foreign_keys=[assigned_to])
    replies = relationship("SupportMessageReply", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SupportMessage(id={self.id}, subject='{self.subject}', status='{self.status}')>"


class SupportMessageReply(BaseModel):
    """Replies to support messages"""
    __tablename__ = "support_message_replies"
    
    message_id = Column(Integer, ForeignKey("support_messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_admin = Column(Boolean, server_default='false', nullable=False)
    reply_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    message = relationship("SupportMessage", back_populates="replies")
    user = relationship("User")
    
    def __repr__(self):
        return f"<SupportMessageReply(id={self.id}, message_id={self.message_id}, is_admin={self.is_admin})>"
