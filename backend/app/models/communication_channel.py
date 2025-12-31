from sqlalchemy import Column, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class CommunicationChannel(Base):
    __tablename__ = "communication_channels"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    channel_type = Column(String, nullable=False)  # telegram, slack, webchat, whatsapp
    is_active = Column(Boolean, default=True)
    config = Column(JSON)  # Store channel-specific configuration
    webhook_url = Column(String, nullable=True)
    bot_token = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    agents = relationship("Agent", back_populates="communication_channels")

class TelegramChannel(Base):
    __tablename__ = "telegram_channels"

    id = Column(String, primary_key=True, index=True)
    channel_id = Column(String, unique=True, index=True)
    bot_token = Column(String, nullable=False)
    webhook_url = Column(String, nullable=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SlackChannel(Base):
    __tablename__ = "slack_channels"

    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    bot_token = Column(String, nullable=False)
    signing_secret = Column(String, nullable=False)
    app_token = Column(String, nullable=True)
    webhook_url = Column(String, nullable=True)
    channel_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WebChatChannel(Base):
    __tablename__ = "webchat_channels"

    id = Column(String, primary_key=True, index=True)
    domain = Column(String, nullable=False)
    embed_code = Column(Text, nullable=False)
    widget_id = Column(String, unique=True, index=True)
    theme_config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WhatsAppChannel(Base):
    __tablename__ = "whatsapp_channels"

    id = Column(String, primary_key=True, index=True)
    phone_number_id = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    webhook_verify_token = Column(String, nullable=False)
    webhook_url = Column(String, nullable=True)
    business_account_id = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())