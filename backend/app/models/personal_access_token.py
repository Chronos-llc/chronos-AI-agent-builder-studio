from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
import secrets
import hashlib

from app.models.base import BaseModel


class PersonalAccessToken(BaseModel):
    __tablename__ = "personal_access_tokens"
    
    # Token information
    name = Column(String(100), nullable=False)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    token_prefix = Column(String(10), nullable=False)  # First few chars for identification
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="personal_access_tokens")
    
    # Token metadata
    scopes = Column(Text, nullable=True)  # JSON string of scopes/permissions
    last_used_at = Column(String(20), nullable=True)  # ISO datetime string
    expires_at = Column(String(20), nullable=True)  # ISO datetime string, None for no expiry
    
    # Status
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<PersonalAccessToken(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    @staticmethod
    def generate_token():
        """Generate a new secure token"""
        # Generate a 32-byte random token
        token = secrets.token_urlsafe(32)
        return f"chronos_{token}"
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def get_token_prefix(token: str) -> str:
        """Get the first 8 characters of the token for identification"""
        return token[:8] if len(token) >= 8 else token
