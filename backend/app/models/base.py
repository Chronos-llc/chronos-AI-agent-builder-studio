from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin

from app.core.database import Base


@declarative_mixin
class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base, TimestampMixin):
    """Base model class with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"