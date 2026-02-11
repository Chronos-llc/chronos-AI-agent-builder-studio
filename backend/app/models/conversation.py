from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class ConversationChannelType(str, enum.Enum):
    WEBCHAT = "webchat"
    SLACK = "slack"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    DISCORD = "discord"
    MESSAGING_API = "messaging_api"
    VOICE = "voice"


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DialogueSessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class Conversation(BaseModel):
    __tablename__ = "conversations"

    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    channel_type = Column(SQLEnum(ConversationChannelType), nullable=False, index=True)
    external_conversation_id = Column(String(255), nullable=True, index=True)
    title = Column(String(255), nullable=True)
    status = Column(SQLEnum(ConversationStatus), nullable=False, default=ConversationStatus.ACTIVE, index=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    context_summary = Column(Text, nullable=True)
    context_tokens_used = Column(Integer, nullable=False, default=0)
    context_tokens_max = Column(Integer, nullable=False, default=16000)

    agent = relationship("AgentModel", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")
    actions = relationship("ConversationAction", back_populates="conversation", cascade="all, delete-orphan")
    dialogues = relationship("ConversationDialogue", back_populates="conversation", cascade="all, delete-orphan")
    dialogue_sessions = relationship("DialogueSession", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index(
            "idx_conversation_agent_user_channel_ext",
            "agent_id",
            "user_id",
            "channel_type",
            "external_conversation_id",
        ),
    )


class ConversationMessage(BaseModel):
    __tablename__ = "conversation_messages"

    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    message_metadata = Column("metadata", JSON, nullable=True)
    tokens_estimate = Column(Integer, nullable=False, default=0)
    source_platform_message_id = Column(String(255), nullable=True)

    conversation = relationship("Conversation", back_populates="messages")


class ConversationAction(BaseModel):
    __tablename__ = "conversation_actions"

    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="pending")

    conversation = relationship("Conversation", back_populates="actions")


class ConversationDialogue(BaseModel):
    __tablename__ = "conversation_dialogues"

    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    dialogue_id = Column(String(128), nullable=False, index=True)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)

    conversation = relationship("Conversation", back_populates="dialogues")


class DialogueSession(BaseModel):
    __tablename__ = "dialogue_sessions"

    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(DialogueSessionStatus), nullable=False, default=DialogueSessionStatus.ACTIVE, index=True)
    model = Column(String(100), nullable=False, default="gpt-4o")
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    conversation = relationship("Conversation", back_populates="dialogue_sessions")
    agent = relationship("AgentModel", back_populates="dialogue_sessions")
    messages = relationship("DialogueMessage", back_populates="session", cascade="all, delete-orphan")


class DialogueMessage(BaseModel):
    __tablename__ = "dialogue_messages"

    session_id = Column(Integer, ForeignKey("dialogue_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)

    session = relationship("DialogueSession", back_populates="messages")
