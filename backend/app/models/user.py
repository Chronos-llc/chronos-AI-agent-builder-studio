from sqlalchemy import Column, String, Boolean, Integer, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Security
    login_attempts = Column(Integer, default=0)
    locked_until = Column(String(20), nullable=True)  # ISO datetime string
    
    # Preferences
    theme = Column(String(20), default="light")  # light, dark, system
    language = Column(String(10), default="en")
    
    # Relationships
    agents = relationship("AgentModel", back_populates="owner", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")
    plan = relationship("UserPlan", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"