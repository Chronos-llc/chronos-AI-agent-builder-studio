import httpx
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.models.integration import IntegrationConfig as IntegrationConfigModel


logger = logging.getLogger(__name__)


class CommunicationChannelConfig(BaseModel):
    channel_type: str = Field(..., description="Channel type: telegram, slack, whatsapp, discord, webchat")
    channel_id: str = Field(..., description="Channel identifier")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for incoming messages")
    access_token: Optional[str] = Field(None, description="Access token for API")
    bot_token: Optional[str] = Field(None, description="Bot token for bot-based channels")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    timeout: int = Field(30, description="Request timeout in seconds")
    
    # Telegram-specific
    telegram_bot_username: Optional[str] = Field(None, description="Telegram bot username")
    telegram_webhook_secret: Optional[str] = Field(None, description="Telegram webhook secret token")
    
    # Slack-specific
    slack_client_id: Optional[str] = Field(None, description="Slack client ID")
    slack_client_secret: Optional[str] = Field(None, description="Slack client secret")
    slack_signing_secret: Optional[str] = Field(None, description="Slack signing secret")
    slack_redirect_uri: Optional[str] = Field(None, description="Slack OAuth redirect URI")
    
    # WhatsApp-specific
    whatsapp_phone_number_id: Optional[str] = Field(None, description="WhatsApp phone number ID")
    whatsapp_business_account_id: Optional[str] = Field(None, description="WhatsApp business account ID")
    whatsapp_template_namespace: Optional[str] = Field(None, description="WhatsApp template namespace")
    
    # Discord-specific
    discord_client_id: Optional[str] = Field(None, description="Discord client ID")
    discord_client_secret: Optional[str] = Field(None, description="Discord client secret")
    discord_redirect_uri: Optional[str] = Field(None, description="Discord OAuth redirect URI")
    discord_permissions: Optional[int] = Field(None, description="Discord bot permissions")
    
    # WebChat-specific
    webchat_config: Optional[Dict[str, Any]] = Field(None, description="WebChat configuration")
    
    # Message routing and analytics
    routing_rules: Optional[List[Dict[str, Any]]] = Field(None, description="Message routing rules")
    analytics_enabled: bool = Field(True, description="Enable analytics tracking")
    rate_limit: Optional[int] = Field(None, description="Rate limit in messages per minute")
    
    # Security and privacy
    encryption_enabled: bool = Field(True, description="Enable end-to-end encryption")
    data_retention_days: int = Field(30, description="Data retention period in days")
    privacy_compliance: Optional[List[str]] = Field(None, description="Privacy compliance standards")


class CommunicationMessage(BaseModel):
    content: str
    channel_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    message_type: str = Field("text", description="Message type: text, image, video, audio, file, command")
    timestamp: Optional[str] = Field(None, description="Message timestamp")
    sender: Optional[str] = Field(None, description="Message sender identifier")
    
    # Routing information
    route_to: Optional[List[str]] = Field(None, description="Target channels for message routing")
    priority: int = Field(1, description="Message priority (1-5)")
    
    # Analytics tracking
    analytics_id: Optional[str] = Field(None, description="Analytics tracking ID")
    source_platform: Optional[str] = Field(None, description="Source platform")
    
    # Media handling
    media_url: Optional[str] = Field(None, description="Media URL")
    media_type: Optional[str] = Field(None, description="Media MIME type")
    file_name: Optional[str] = Field(None, description="File name for attachments")
    file_size: Optional[int] = Field(None, description="File size in bytes")


class CommunicationChannelError(Exception):
    """Custom exception for communication channel errors"""
    pass

class MessageAnalytics(BaseModel):
    """Message analytics data"""
    message_id: str
    channel_type: str
    channel_id: str
    user_id: Optional[str] = None
    timestamp: str
    
    # Delivery metrics
    delivered: bool = False
    read: bool = False
    delivery_time_ms: Optional[float] = None
    read_time_ms: Optional[float] = None
    
    # Engagement metrics
    response_time_ms: Optional[float] = None
    user_response: Optional[str] = None
    
    # Error tracking
    error_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[str] = None
    
    # Performance metrics
    processing_time_ms: Optional[float] = None
    queue_time_ms: Optional[float] = None
    
    # Content analysis
    message_length: int = 0
    sentiment_score: Optional[float] = None
    intent: Optional[str] = None
    entities: Optional[List[str]] = None

class RoutingRule(BaseModel):
    """Message routing rule"""
    name: str
    condition: Dict[str, Any]
    target_channels: List[str]
    priority: int = 1
    enabled: bool = True
    
    # Advanced routing options
    fallback_channels: Optional[List[str]] = None
    max_retries: int = 3
    retry_delay_ms: int = 1000
    timeout_ms: int = 30000

class ChannelAnalytics(BaseModel):
    """Channel performance analytics"""
    channel_id: str
    channel_type: str
    
    # Usage statistics
    total_messages: int = 0
    successful_messages: int = 0
    failed_messages: int = 0
    
    # Performance metrics
    avg_response_time_ms: float = 0.0
    avg_delivery_time_ms: float = 0.0
    uptime_percentage: float = 100.0
    
    # User engagement
    active_users: int = 0
    daily_active_users: int = 0
    weekly_active_users: int = 0
    
    # Error tracking
    error_rate: float = 0.0
    last_error_time: Optional[str] = None
    common_errors: Optional[Dict[str, int]] = None
    
    # Timestamps
    created_at: str
    updated_at: str


class CommunicationChannelManager:
    """
    Manager for communication channels
    
    Handles multiple communication channel integrations and provides a unified interface
    for sending and receiving messages with advanced routing and analytics.
    """

    def __init__(self):
        self.channels: Dict[str, CommunicationChannelConfig] = {}
        self.default_channel: Optional[str] = None
        self.routing_rules: Dict[str, List[RoutingRule]] = {}
        self.message_analytics: Dict[str, MessageAnalytics] = {}
        self.channel_analytics: Dict[str, ChannelAnalytics] = {}
        self.message_queue: Dict[str, List[CommunicationMessage]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize analytics for all channels
        self._initialize_analytics()

    def _initialize_analytics(self):
        """Initialize analytics tracking for all channels"""
        from datetime import datetime
        
        # Initialize default analytics structure
        for channel_id, config in self.channels.items():
            self._initialize_channel_analytics(channel_id, config.channel_type)
    
    def _initialize_channel_analytics(self, channel_id: str, channel_type: str):
        """Initialize analytics for a specific channel"""
        from datetime import datetime
        
        now = datetime.now().isoformat()
        
        self.channel_analytics[channel_id] = ChannelAnalytics(
            channel_id=channel_id,
            channel_type=channel_type,
            created_at=now,
            updated_at=now
        )
    
    async def add_channel(self, channel_id: str, config: CommunicationChannelConfig):
        """Add a new communication channel"""
        # Validate the configuration
        supported_types = ["telegram", "slack", "whatsapp", "discord", "webchat"]
        if config.channel_type not in supported_types:
            raise CommunicationChannelError(f"Unsupported channel type: {config.channel_type}. Supported types: {', '.join(supported_types)}")
        
        # Channel-specific validation
        if config.channel_type == "telegram":
            if not config.bot_token:
                raise CommunicationChannelError("Bot token required for Telegram")
            if not config.telegram_bot_username:
                raise CommunicationChannelError("Telegram bot username required")
        
        elif config.channel_type == "slack":
            if not config.bot_token and not config.access_token:
                raise CommunicationChannelError("Bot token or access token required for Slack")
            if not config.slack_client_id or not config.slack_client_secret:
                raise CommunicationChannelError("Slack OAuth credentials required")
        
        elif config.channel_type == "whatsapp":
            if not config.api_key:
                raise CommunicationChannelError("API key required for WhatsApp")
            if not config.whatsapp_phone_number_id or not config.whatsapp_business_account_id:
                raise CommunicationChannelError("WhatsApp phone number ID and business account ID required")
        
        elif config.channel_type == "discord":
            if not config.bot_token:
                raise CommunicationChannelError("Bot token required for Discord")
            if not config.discord_client_id or not config.discord_client_secret:
                raise CommunicationChannelError("Discord OAuth credentials required")
        
        elif config.channel_type == "webchat":
            if not config.webchat_config:
                raise CommunicationChannelError("WebChat configuration required")
        
        # Initialize message queue for this channel
        self.message_queue[channel_id] = []
        
        # Store the channel configuration
        self.channels[channel_id] = config
        
        # Initialize analytics for this channel
        self._initialize_channel_analytics(channel_id, config.channel_type)
        
        # Set as default if it's the first channel
        if not self.default_channel:
            self.default_channel = channel_id
        
        logger.info(f"Added {config.channel_type} channel: {channel_id}")

    async def remove_channel(self, channel_id: str):
        """Remove a communication channel"""
        if channel_id in self.channels:
            del self.channels[channel_id]
            
            # Update default channel if needed
            if self.default_channel == channel_id:
                self.default_channel = next(iter(self.channels.keys()), None)

    async def get_channel(self, channel_id: Optional[str] = None) -> CommunicationChannelConfig:
        """Get a communication channel configuration"""
        if not channel_id:
            if not self.default_channel:
                raise CommunicationChannelError("No default communication channel configured")
            return self.channels[self.default_channel]
        
        if channel_id not in self.channels:
            raise CommunicationChannelError(f"Communication channel {channel_id} not found")
        
        return self.channels[channel_id]

    async def list_channels(self) -> List[Dict[str, Any]]:
        """List all configured communication channels"""
        return [
            {
                "channel_id": channel_id,
                "config": config.dict(),
                "is_default": channel_id == self.default_channel
            }
            for channel_id, config in self.channels.items()
        ]

    async def send_message(
        self,
        message: CommunicationMessage,
        channel_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message through the specified communication channel with advanced routing"""
        from datetime import datetime
        import uuid
        
        # Generate analytics ID if not provided
        if not message.analytics_id:
            message.analytics_id = str(uuid.uuid4())
        
        # Set timestamp if not provided
        if not message.timestamp:
            message.timestamp = datetime.now().isoformat()
        
        # Apply message routing if route_to is specified
        target_channels = message.route_to or []
        if target_channels:
            results = []
            for target_channel_id in target_channels:
                if target_channel_id in self.channels:
                    try:
                        result = await self._send_to_channel(target_channel_id, message)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Failed to send message to {target_channel_id}: {str(e)}")
                        results.append({
                            "success": False,
                            "channel_id": target_channel_id,
                            "error": str(e)
                        })
                else:
                    results.append({
                        "success": False,
                        "channel_id": target_channel_id,
                        "error": f"Channel {target_channel_id} not found"
                    })
            
            return {
                "success": any(result.get("success", False) for result in results),
                "results": results,
                "analytics_id": message.analytics_id
            }
        
        # Use specified channel or default channel
        config = await self.get_channel(channel_id)
        
        # Apply routing rules if available
        if config.routing_rules:
            routed_results = await self._apply_routing_rules(message, config)
            return routed_results
        
        # Send to the specified channel
        return await self._send_to_channel(config.channel_id, message)
    
    async def _send_to_channel(self, channel_id: str, message: CommunicationMessage) -> Dict[str, Any]:
        """Send message to a specific channel"""
        if channel_id not in self.channels:
            raise CommunicationChannelError(f"Channel {channel_id} not found")
        
        config = self.channels[channel_id]
        
        # Track message in analytics
        await self._track_message_analytics(channel_id, message, "sent")
        
        try:
            if config.channel_type == "telegram":
                result = await self._send_telegram_message(config, message)
            elif config.channel_type == "slack":
                result = await self._send_slack_message(config, message)
            elif config.channel_type == "whatsapp":
                result = await self._send_whatsapp_message(config, message)
            elif config.channel_type == "discord":
                result = await self._send_discord_message(config, message)
            elif config.channel_type == "webchat":
                result = await self._send_webchat_message(config, message)
            else:
                raise CommunicationChannelError(f"Unsupported channel type: {config.channel_type}")
            
            # Update analytics on successful send
            await self._track_message_analytics(channel_id, message, "delivered")
            return result
            
        except Exception as e:
            # Update analytics on failure
            await self._track_message_analytics(channel_id, message, "failed", str(e))
            raise CommunicationChannelError(f"Failed to send message via {config.channel_type}: {str(e)}")
    
    async def _apply_routing_rules(self, message: CommunicationMessage, config: CommunicationChannelConfig) -> Dict[str, Any]:
        """Apply routing rules to determine target channels"""
        results = []
        
        # Check if routing rules are defined in config
        if not config.routing_rules:
            return await self._send_to_channel(config.channel_id, message)
        
        # Apply each routing rule
        for rule_data in config.routing_rules:
            try:
                rule = RoutingRule(**rule_data)
                if not rule.enabled:
                    continue
                
                # Check if message matches routing condition
                if self._check_routing_condition(message, rule.condition):
                    for target_channel_id in rule.target_channels:
                        if target_channel_id in self.channels:
                            try:
                                result = await self._send_to_channel(target_channel_id, message)
                                results.append(result)
                                # If not a fallback scenario, break after first successful delivery
                                if not rule.fallback_channels:
                                    break
                            except Exception as e:
                                logger.warning(f"Routing to {target_channel_id} failed: {str(e)}")
                                # Try fallback channels if available
                                if rule.fallback_channels:
                                    for fallback_channel_id in rule.fallback_channels:
                                        if fallback_channel_id in self.channels:
                                            try:
                                                fallback_result = await self._send_to_channel(fallback_channel_id, message)
                                                results.append(fallback_result)
                                                break
                                            except Exception as fe:
                                                logger.error(f"Fallback to {fallback_channel_id} failed: {str(fe)}")
                
            except Exception as e:
                logger.error(f"Error applying routing rule {rule.name}: {str(e)}")
        
        if not results:
            # No routing rules matched, send to default channel
            result = await self._send_to_channel(config.channel_id, message)
            results.append(result)
        
        return {
            "success": any(result.get("success", False) for result in results),
            "results": results,
            "routing_applied": True,
            "analytics_id": message.analytics_id
        }
    
    def _check_routing_condition(self, message: CommunicationMessage, condition: Dict[str, Any]) -> bool:
        """Check if message matches routing condition"""
        try:
            # Simple condition checking
            for key, expected_value in condition.items():
                if key == "message_type":
                    if message.message_type != expected_value:
                        return False
                elif key == "priority":
                    if message.priority < expected_value:
                        return False
                elif key == "content_contains":
                    if expected_value not in message.content:
                        return False
                elif key == "sender":
                    if message.sender != expected_value:
                        return False
                elif key == "channel_id":
                    if message.channel_id != expected_value:
                        return False
                elif key == "user_id":
                    if message.user_id != expected_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking routing condition: {str(e)}")
            return False

    async def _send_telegram_message(
        self,
        config: CommunicationChannelConfig,
        message: CommunicationMessage
    ) -> Dict[str, Any]:
        """Send a message through Telegram"""
        try:
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"
                
                payload = {
                    "chat_id": message.channel_id or config.channel_id,
                    "text": message.content
                }
                
                if message.metadata:
                    payload.update(message.metadata)
                
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("ok"):
                    return {
                        "success": True,
                        "message_id": result["result"]["message_id"],
                        "channel": "telegram",
                        "timestamp": result["result"]["date"]
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("description", "Unknown error"),
                        "channel": "telegram"
                    }
        
        except Exception as e:
            raise CommunicationChannelError(f"Telegram message failed: {str(e)}")

    async def _send_slack_message(
        self,
        config: CommunicationChannelConfig,
        message: CommunicationMessage
    ) -> Dict[str, Any]:
        """Send a message through Slack"""
        try:
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                url = "https://slack.com/api/chat.postMessage"
                
                payload = {
                    "channel": message.channel_id or config.channel_id,
                    "text": message.content
                }
                
                if message.metadata:
                    payload.update(message.metadata)
                
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Authorization": f"Bearer {config.access_token}"}
                )
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("ok"):
                    return {
                        "success": True,
                        "message_id": result["ts"],
                        "channel": result["channel"],
                        "timestamp": result["ts"]
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Unknown error"),
                        "channel": "slack"
                    }
        
        except Exception as e:
            raise CommunicationChannelError(f"Slack message failed: {str(e)}")

    async def _send_whatsapp_message(
        self,
        config: CommunicationChannelConfig,
        message: CommunicationMessage
    ) -> Dict[str, Any]:
        """Send a message through WhatsApp Business API"""
        try:
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                # WhatsApp Business API endpoint
                url = f"https://graph.facebook.com/v18.0/{config.channel_id}/messages"
                
                payload = {
                    "messaging_product": "whatsapp",
                    "to": message.user_id,
                    "type": "text",
                    "text": {"body": message.content}
                }
                
                if message.metadata:
                    payload.update(message.metadata)
                
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Authorization": f"Bearer {config.api_key}"}
                )
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("messages"):
                    return {
                        "success": True,
                        "message_id": result["messages"][0]["id"],
                        "channel": "whatsapp",
                        "timestamp": result["messages"][0]["timestamp"]
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", {}).get("message", "Unknown error"),
                        "channel": "whatsapp"
                    }
        
        except Exception as e:
            raise CommunicationChannelError(f"WhatsApp message failed: {str(e)}")

    async def _send_discord_message(
        self,
        config: CommunicationChannelConfig,
        message: CommunicationMessage
    ) -> Dict[str, Any]:
        """Send a message through Discord"""
        try:
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                url = f"https://discord.com/api/v10/channels/{message.channel_id or config.channel_id}/messages"
                
                payload = {
                    "content": message.content
                }
                
                # Handle different message types
                if message.message_type == "embed" and message.metadata:
                    payload["embeds"] = [message.metadata]
                elif message.media_url:
                    payload["attachments"] = [{"url": message.media_url}]
                
                if message.metadata:
                    payload.update(message.metadata)
                
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Authorization": f"Bot {config.bot_token}"}
                )
                response.raise_for_status()
                
                result = response.json()
                
                return {
                    "success": True,
                    "message_id": result["id"],
                    "channel": result["channel_id"],
                    "timestamp": result["timestamp"],
                    "channel_type": "discord"
                }
        
        except Exception as e:
            raise CommunicationChannelError(f"Discord message failed: {str(e)}")
    
    async def _send_webchat_message(
        self,
        config: CommunicationChannelConfig,
        message: CommunicationMessage
    ) -> Dict[str, Any]:
        """Send a message through WebChat"""
        try:
            from datetime import datetime
            
            # In a real implementation, this would use WebSocket or direct API call
            # For now, we'll simulate the WebChat message delivery
            
            webchat_config = config.webchat_config or {}
            session_id = message.channel_id or f"webchat_{datetime.now().timestamp()}"
            
            # Simulate message delivery to WebChat
            result = {
                "success": True,
                "message_id": f"webchat_{datetime.now().timestamp()}",
                "session_id": session_id,
                "channel": "webchat",
                "timestamp": datetime.now().isoformat(),
                "delivered_via": "websocket"
            }
            
            # Update WebChat session if it exists
            if session_id in webchat_manager.sessions:
                webchat_session = webchat_manager.sessions[session_id]
                webchat_message = WebChatMessage(
                    message_id=result["message_id"],
                    content=message.content,
                    sender="bot",
                    timestamp=result["timestamp"],
                    metadata=message.metadata or {}
                )
                webchat_session.messages.append(webchat_message)
            
            return result
            
        except Exception as e:
            raise CommunicationChannelError(f"WebChat message failed: {str(e)}")
    
    async def _track_message_analytics(self, channel_id: str, message: CommunicationMessage, status: str, error: Optional[str] = None):
        """Track message analytics"""
        from datetime import datetime
        
        analytics_id = message.analytics_id or f"msg_{datetime.now().timestamp()}"
        
        # Initialize or update message analytics
        if analytics_id not in self.message_analytics:
            self.message_analytics[analytics_id] = MessageAnalytics(
                message_id=analytics_id,
                channel_type=self.channels[channel_id].channel_type,
                channel_id=channel_id,
                user_id=message.user_id,
                timestamp=message.timestamp or datetime.now().isoformat(),
                message_length=len(message.content or "")
            )
        
        analytics = self.message_analytics[analytics_id]
        
        # Update status
        if status == "delivered":
            analytics.delivered = True
            analytics.delivery_time_ms = (datetime.now() - datetime.fromisoformat(analytics.timestamp)).total_seconds() * 1000
        elif status == "read":
            analytics.read = True
            analytics.read_time_ms = (datetime.now() - datetime.fromisoformat(analytics.timestamp)).total_seconds() * 1000
        elif status == "failed":
            analytics.error_count += 1
            analytics.last_error = error
            analytics.last_error_time = datetime.now().isoformat()
        
        # Update channel analytics
        if channel_id in self.channel_analytics:
            channel_analytics = self.channel_analytics[channel_id]
            channel_analytics.total_messages += 1
            
            if status == "delivered":
                channel_analytics.successful_messages += 1
            elif status == "failed":
                channel_analytics.failed_messages += 1
                channel_analytics.error_rate = channel_analytics.failed_messages / max(channel_analytics.total_messages, 1)
            
            # Update common errors
            if error and status == "failed":
                if not channel_analytics.common_errors:
                    channel_analytics.common_errors = {}
                
                error_key = error.split(":")[0] if ":" in error else error
                channel_analytics.common_errors[error_key] = channel_analytics.common_errors.get(error_key, 0) + 1
            
            channel_analytics.updated_at = datetime.now().isoformat()
        
        logger.debug(f"Tracked {status} message {analytics_id} on channel {channel_id}")

    async def receive_webhook(
        self,
        channel_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process incoming webhook messages"""
        if channel_id not in self.channels:
            raise CommunicationChannelError(f"Unknown channel: {channel_id}")
        
        config = self.channels[channel_id]
        
        # Process different webhook formats based on channel type
        if config.channel_type == "telegram":
            return self._process_telegram_webhook(payload)
        elif config.channel_type == "slack":
            return self._process_slack_webhook(payload)
        elif config.channel_type == "whatsapp":
            return self._process_whatsapp_webhook(payload)
        elif config.channel_type == "discord":
            return self._process_discord_webhook(payload)
        else:
            raise CommunicationChannelError(f"Unsupported channel type for webhook: {config.channel_type}")

    def _process_telegram_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process Telegram webhook payload"""
        try:
            message = payload.get("message", {})
            
            return {
                "channel": "telegram",
                "message_id": message.get("message_id"),
                "chat_id": message.get("chat", {}).get("id"),
                "user_id": message.get("from", {}).get("id"),
                "username": message.get("from", {}).get("username"),
                "content": message.get("text"),
                "timestamp": message.get("date"),
                "raw": payload
            }
        except Exception as e:
            raise CommunicationChannelError(f"Failed to process Telegram webhook: {str(e)}")

    def _process_slack_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process Slack webhook payload"""
        try:
            # Handle Slack challenge
            if payload.get("type") == "url_verification":
                return {"challenge": payload.get("challenge")}
            
            event = payload.get("event", {})
            
            return {
                "channel": "slack",
                "message_id": event.get("ts"),
                "channel_id": event.get("channel"),
                "user_id": event.get("user"),
                "content": event.get("text"),
                "timestamp": event.get("ts"),
                "raw": payload
            }
        except Exception as e:
            raise CommunicationChannelError(f"Failed to process Slack webhook: {str(e)}")

    def _process_whatsapp_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process WhatsApp webhook payload"""
        try:
            entry = payload.get("entry", [{}])[0]
            change = entry.get("changes", [{}])[0]
            value = change.get("value", {})
            message = value.get("messages", [{}])[0]
            
            return {
                "channel": "whatsapp",
                "message_id": message.get("id"),
                "phone_number": message.get("from"),
                "user_id": message.get("from"),
                "content": message.get("text", {}).get("body"),
                "timestamp": message.get("timestamp"),
                "raw": payload
            }
        except Exception as e:
            raise CommunicationChannelError(f"Failed to process WhatsApp webhook: {str(e)}")

    def _process_discord_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process Discord webhook payload"""
        try:
            return {
                "channel": "discord",
                "message_id": payload.get("id"),
                "channel_id": payload.get("channel_id"),
                "user_id": payload.get("author", {}).get("id"),
                "username": payload.get("author", {}).get("username"),
                "content": payload.get("content"),
                "timestamp": payload.get("timestamp"),
                "raw": payload
            }
        except Exception as e:
            raise CommunicationChannelError(f"Failed to process Discord webhook: {str(e)}")

    async def close_all(self):
        """Close all communication channel connections"""
        self.channels.clear()
        self.default_channel = None
        self.routing_rules.clear()
        self.message_analytics.clear()
        self.channel_analytics.clear()
        self.message_queue.clear()
        self.active_sessions.clear()
    
    async def add_routing_rule(self, channel_id: str, rule: RoutingRule):
        """Add a routing rule for a specific channel"""
        if channel_id not in self.channels:
            raise CommunicationChannelError(f"Channel {channel_id} not found")
        
        if channel_id not in self.routing_rules:
            self.routing_rules[channel_id] = []
        
        # Check for duplicate rule names
        for existing_rule in self.routing_rules[channel_id]:
            if existing_rule.name == rule.name:
                raise CommunicationChannelError(f"Routing rule {rule.name} already exists for channel {channel_id}")
        
        self.routing_rules[channel_id].append(rule)
        
        # Sort rules by priority (higher priority first)
        self.routing_rules[channel_id].sort(key=lambda x: x.priority, reverse=True)
        
        logger.info(f"Added routing rule {rule.name} for channel {channel_id}")
    
    async def remove_routing_rule(self, channel_id: str, rule_name: str):
        """Remove a routing rule"""
        if channel_id not in self.routing_rules:
            raise CommunicationChannelError(f"No routing rules found for channel {channel_id}")
        
        initial_count = len(self.routing_rules[channel_id])
        self.routing_rules[channel_id] = [
            rule for rule in self.routing_rules[channel_id]
            if rule.name != rule_name
        ]
        
        if len(self.routing_rules[channel_id]) == initial_count:
            raise CommunicationChannelError(f"Routing rule {rule_name} not found for channel {channel_id}")
        
        logger.info(f"Removed routing rule {rule_name} from channel {channel_id}")
    
    async def get_routing_rules(self, channel_id: str) -> List[RoutingRule]:
        """Get routing rules for a channel"""
        if channel_id not in self.routing_rules:
            return []
        return self.routing_rules[channel_id]
    
    async def get_message_analytics(self, analytics_id: str) -> Optional[MessageAnalytics]:
        """Get analytics for a specific message"""
        return self.message_analytics.get(analytics_id)
    
    async def get_channel_analytics(self, channel_id: str) -> Optional[ChannelAnalytics]:
        """Get analytics for a specific channel"""
        return self.channel_analytics.get(channel_id)
    
    async def get_all_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics for all channels"""
        from datetime import datetime
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_channels": len(self.channels),
            "total_messages": sum(len(analytics) for analytics in self.message_analytics.values()),
            "channel_analytics": {
                channel_id: analytics.dict()
                for channel_id, analytics in self.channel_analytics.items()
            },
            "message_analytics": {
                analytics_id: analytics.dict()
                for analytics_id, analytics in self.message_analytics.items()
            },
            "routing_rules": {
                channel_id: [rule.dict() for rule in rules]
                for channel_id, rules in self.routing_rules.items()
            }
        }
    
    async def queue_message(self, channel_id: str, message: CommunicationMessage):
        """Queue a message for delayed processing"""
        if channel_id not in self.message_queue:
            raise CommunicationChannelError(f"Channel {channel_id} not found")
        
        self.message_queue[channel_id].append(message)
        logger.info(f"Queued message {message.analytics_id} for channel {channel_id}")
        
        return {
            "success": True,
            "message_id": message.analytics_id,
            "channel_id": channel_id,
            "queue_position": len(self.message_queue[channel_id])
        }
    
    async def process_queue(self, channel_id: str, batch_size: int = 10) -> Dict[str, Any]:
        """Process queued messages"""
        if channel_id not in self.message_queue:
            raise CommunicationChannelError(f"Channel {channel_id} not found")
        
        processed = 0
        successful = 0
        failed = 0
        results = []
        
        while self.message_queue[channel_id] and processed < batch_size:
            message = self.message_queue[channel_id].pop(0)
            processed += 1
            
            try:
                result = await self.send_message(message, channel_id)
                if result.get("success", False):
                    successful += 1
                else:
                    failed += 1
                results.append(result)
            except Exception as e:
                failed += 1
                results.append({
                    "success": False,
                    "message_id": message.analytics_id,
                    "error": str(e)
                })
                logger.error(f"Failed to process queued message {message.analytics_id}: {str(e)}")
        
        return {
            "processed": processed,
            "successful": successful,
            "failed": failed,
            "results": results,
            "queue_remaining": len(self.message_queue[channel_id])
        }
    
    async def start_session(self, session_id: str, channel_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Start a communication session"""
        if channel_id not in self.channels:
            raise CommunicationChannelError(f"Channel {channel_id} not found")
        
        self.active_sessions[session_id] = {
            "channel_id": channel_id,
            "user_id": user_id,
            "started_at": datetime.now().isoformat(),
            "message_count": 0,
            "status": "active"
        }
        
        logger.info(f"Started session {session_id} on channel {channel_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "channel_id": channel_id,
            "status": "active"
        }
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a communication session"""
        if session_id not in self.active_sessions:
            raise CommunicationChannelError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session["status"] = "ended"
        session["ended_at"] = datetime.now().isoformat()
        
        logger.info(f"Ended session {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "duration_seconds": (datetime.now() - datetime.fromisoformat(session["started_at"])).total_seconds(),
            "message_count": session["message_count"]
        }
    
    async def track_session_message(self, session_id: str, message: CommunicationMessage):
        """Track a message within a session"""
        if session_id not in self.active_sessions:
            raise CommunicationChannelError(f"Session {session_id} not found")
        
        self.active_sessions[session_id]["message_count"] += 1
        self.active_sessions[session_id]["last_message_at"] = datetime.now().isoformat()
        
        # Also track in message analytics
        await self._track_message_analytics(
            self.active_sessions[session_id]["channel_id"],
            message,
            "sent"
        )


# Global communication channel manager instance
communication_manager = CommunicationChannelManager()


async def initialize_communication_channels():
    """Initialize communication channels from configuration"""
    try:
        # In a real implementation, this would load from database/config
        logger.info("Communication channels initialized")
    except Exception as e:
        logger.error(f"Failed to initialize communication channels: {e}")


async def get_communication_manager() -> CommunicationChannelManager:
    """Get the communication channel manager"""
    return communication_manager