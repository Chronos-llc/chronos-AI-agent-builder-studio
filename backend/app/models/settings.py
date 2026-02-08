from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class UserSettings(BaseModel):
    __tablename__ = "user_settings"
    
    # Settings key-value pairs
    setting_key = Column(String(100), nullable=False, index=True)
    setting_value = Column(JSON, nullable=True)
    setting_type = Column(String(50), nullable=False)  # string, number, boolean, object, array
    
    # Scope
    is_global = Column(Boolean, default=False)  # True for global settings, False for user-specific
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for global settings
    
    # Relationships
    user = relationship("User", back_populates="settings")
    
    def __repr__(self):
        return f"<UserSettings(key='{self.setting_key}', user_id={self.user_id})>"


# Add settings relationship to User model
# This needs to be added to the User model file
# settings = relationship("UserSettings", back_populates="user", cascade="all, delete-orphan")