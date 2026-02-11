from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.models.base import BaseModel
from app.models.user import User


class PlatformUpdate(BaseModel):
    """Platform update model for system announcements and news"""
    __tablename__ = "platform_updates"
    
    # Basic information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    update_type = Column(String(20), nullable=False)  # e.g., FEATURE, BUG_FIX, ANNOUNCEMENT
    priority = Column(String(20), server_default='NORMAL', nullable=False)  # LOW, NORMAL, HIGH, CRITICAL
    
    # Media
    media_type = Column(String(20), nullable=True)  # IMAGE, VIDEO, NONE
    media_urls = Column(JSON, nullable=True)  # Array of media URLs
    thumbnail_url = Column(String(500), nullable=True)
    
    # Visibility
    is_published = Column(Boolean, server_default='false', nullable=False)
    target_audience = Column(String(20), server_default='ALL', nullable=False)  # ALL, ADMIN, USER
    
    # Tracking
    view_count = Column(Integer, server_default='0', nullable=False)
    
    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user_views = relationship("UserUpdateView", back_populates="update", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PlatformUpdate(id={self.id}, title='{self.title}', status='{'published' if self.is_published else 'draft'}')>"


class UserUpdateView(BaseModel):
    """Track which users have viewed which updates"""
    __tablename__ = "user_update_views"
    
    update_id = Column(Integer, ForeignKey("platform_updates.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    update = relationship("PlatformUpdate", back_populates="user_views")
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserUpdateView(id={self.id}, update_id={self.update_id}, user_id={self.user_id})>"
