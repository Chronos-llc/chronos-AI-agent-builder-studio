"""
Marketplace Database Models

Defines the database models for marketplace listings, installations, and reviews.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class MarketplaceCategory(BaseModel):
    """Marketplace category model for organizing agents"""
    __tablename__ = "marketplace_categories"
    
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    is_active = Column(Boolean, server_default='true', nullable=False)
    sort_order = Column(Integer, server_default='0', nullable=False)
    
    # Relationships
    listings = relationship("MarketplaceListing", back_populates="category_obj")
    
    def __repr__(self):
        return f"<MarketplaceCategory(id={self.id}, name='{self.name}')>"


class MarketplaceTag(BaseModel):
    """Marketplace tag model for filtering and searching"""
    __tablename__ = "marketplace_tags"
    
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, server_default='true', nullable=False)
    usage_count = Column(Integer, server_default='0', nullable=False)
    
    # Relationships
    listings = relationship("MarketplaceListing", secondary="marketplace_listing_tags", back_populates="tags_obj")
    
    def __repr__(self):
        return f"<MarketplaceTag(id={self.id}, name='{self.name}')>"


class MarketplaceListingTag(BaseModel):
    """Association table for marketplace listings and tags"""
    __tablename__ = "marketplace_listing_tags"
    
    listing_id = Column(Integer, ForeignKey("marketplace_listings.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("marketplace_tags.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MarketplaceListing(BaseModel):
    """Marketplace listing model for published agents"""
    __tablename__ = "marketplace_listings"
    
    # Basic information
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    listing_type = Column(String(20), nullable=False)  # 'AGENT' or 'SUBAGENT'
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("marketplace_categories.id", ondelete="SET NULL"), nullable=True)
    
    # Visibility & Moderation
    visibility = Column(String(20), server_default='PUBLIC', nullable=False)
    moderation_status = Column(String(20), server_default='PENDING', nullable=False)
    moderation_notes = Column(Text, nullable=True)
    
    # Metadata
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(20), nullable=True)
    schema_data = Column(JSON, nullable=True)
    preview_images = Column(JSON, nullable=True)
    demo_video_url = Column(String(500), nullable=True)
    
    # Statistics
    install_count = Column(Integer, server_default='0', nullable=False)
    rating_average = Column(Numeric(3, 2), server_default='0.0', nullable=False)
    rating_count = Column(Integer, server_default='0', nullable=False)
    view_count = Column(Integer, server_default='0', nullable=False)
    
    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    agent = relationship("AgentModel", foreign_keys=[agent_id])
    author = relationship("User", foreign_keys=[author_id])
    category_obj = relationship("MarketplaceCategory", back_populates="listings")
    tags_obj = relationship("MarketplaceTag", secondary="marketplace_listing_tags", back_populates="listings")
    installations = relationship("MarketplaceInstallation", back_populates="listing", cascade="all, delete-orphan")
    reviews = relationship("MarketplaceReview", back_populates="listing", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MarketplaceListing(id={self.id}, title='{self.title}', status='{self.moderation_status}')>"


class MarketplaceInstallation(BaseModel):
    """Marketplace installation tracking"""
    __tablename__ = "marketplace_installations"
    
    listing_id = Column(Integer, ForeignKey("marketplace_listings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    installed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    listing = relationship("MarketplaceListing", back_populates="installations")
    user = relationship("User")
    agent = relationship("AgentModel")
    
    def __repr__(self):
        return f"<MarketplaceInstallation(id={self.id}, listing_id={self.listing_id}, user_id={self.user_id})>"


class MarketplaceReview(BaseModel):
    """Marketplace review and rating"""
    __tablename__ = "marketplace_reviews"
    
    listing_id = Column(Integer, ForeignKey("marketplace_listings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    review_text = Column(Text, nullable=True)
    
    # Relationships
    listing = relationship("MarketplaceListing", back_populates="reviews")
    user = relationship("User")
    
    def __repr__(self):
        return f"<MarketplaceReview(id={self.id}, listing_id={self.listing_id}, rating={self.rating})>"
