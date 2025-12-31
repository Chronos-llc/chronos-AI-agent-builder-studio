from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CommunicationChannelBase(BaseModel):
    """Base communication channel schema with common fields."""
    name: str = Field(..., description="Channel name")
    type: str = Field(..., description="Channel type: telegram, slack, webchat, whatsapp")
    description: Optional[str] = Field(None, description="Channel description")
    is_active: bool = Field(True, description="Whether the channel is active")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Channel-specific configuration")


class CommunicationChannelCreate(CommunicationChannelBase):
    """Schema for creating a communication channel."""
    agent_id: Optional[int] = Field(None, description="Associated agent ID")


class CommunicationChannelUpdate(BaseModel):
    """Schema for updating a communication channel."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    configuration: Optional[Dict[str, Any]] = None


class CommunicationChannel(CommunicationChannelBase):
    """Schema for communication channel with database fields."""
    id: int
    agent_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebChatChannelCreate(BaseModel):
    """Schema for creating a web chat channel."""
    agent_id: int
    name: str = Field(default="WebChat", description="Channel name")
    description: Optional[str] = Field(None, description="Channel description")
    theme: Dict[str, Any] = Field(
        default_factory=lambda: {
            "primaryColor": "#3b82f6",
            "backgroundColor": "#ffffff",
            "textColor": "#1f2937",
            "botMessageColor": "#f3f4f6",
            "userMessageColor": "#3b82f6"
        },
        description="Chat widget theme configuration"
    )
    position: str = Field(default="bottom-right", description="Widget position: bottom-right, bottom-left, top-right, top-left")
    show_avatar: bool = Field(True, description="Whether to show agent avatar")
    welcome_message: Optional[str] = Field(None, description="Welcome message for new users")


class WebChatConfiguration(BaseModel):
    """Schema for web chat configuration."""
    theme: Dict[str, Any]
    position: str
    show_avatar: bool
    welcome_message: Optional[str]
    custom_css: Optional[str] = Field(None, description="Custom CSS for the chat widget")
    embed_code: str = Field(..., description="HTML embed code for the chat widget")


class TelegramChannelCreate(BaseModel):
    """Schema for creating a Telegram channel."""
    agent_id: int
    bot_token: str = Field(..., description="Telegram bot token")
    bot_username: Optional[str] = Field(None, description="Telegram bot username")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for receiving messages")
    commands: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom bot commands and descriptions"
    )


class SlackChannelCreate(BaseModel):
    """Schema for creating a Slack channel."""
    agent_id: int
    bot_token: str = Field(..., description="Slack bot token")
    signing_secret: str = Field(..., description="Slack signing secret")
    client_id: Optional[str] = Field(None, description="Slack app client ID")
    client_secret: Optional[str] = Field(None, description="Slack app client secret")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")


class WhatsAppChannelCreate(BaseModel):
    """Schema for creating a WhatsApp channel."""
    agent_id: int
    phone_number_id: str = Field(..., description="WhatsApp Business phone number ID")
    access_token: str = Field(..., description="WhatsApp Business API access token")
    verify_token: Optional[str] = Field(None, description="Webhook verification token")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for receiving messages")
    business_name: Optional[str] = Field(None, description="Business name")
    business_description: Optional[str] = Field(None, description="Business description")