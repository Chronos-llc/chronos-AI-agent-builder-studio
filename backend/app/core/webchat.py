import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import logging


logger = logging.getLogger(__name__)


class WebChatConfig(BaseModel):
    embed_type: str = Field("bubble", description="Embed type: bubble, iframe, standalone, react")
    theme: Dict[str, Any] = Field(
        {
            "primary_color": "#4F46E5",
            "secondary_color": "#1F2937",
            "text_color": "#FFFFFF",
            "background_color": "#FFFFFF"
        },
        description="Theme configuration"
    )
    position: str = Field("bottom_right", description="Position for bubble embed")
    mobile_responsive: bool = Field(True, description="Enable mobile responsiveness")
    accessibility_features: Dict[str, bool] = Field(
        {
            "high_contrast": False,
            "screen_reader_support": True,
            "keyboard_navigation": True
        },
        description="Accessibility features"
    )
    custom_css: Optional[str] = Field(None, description="Custom CSS for styling")
    custom_js: Optional[str] = Field(None, description="Custom JavaScript")
    
    # Advanced features
    voice_input_enabled: bool = Field(False, description="Enable voice input")
    voice_output_enabled: bool = Field(False, description="Enable voice output")
    voice_language: str = Field("en-US", description="Voice language code")
    voice_rate: float = Field(1.0, description="Voice speech rate")
    voice_pitch: float = Field(1.0, description="Voice speech pitch")
    
    # User feedback
    feedback_enabled: bool = Field(True, description="Enable user feedback collection")
    feedback_types: List[str] = Field(["thumbs_up", "thumbs_down", "text"], description="Available feedback types")
    
    # Analytics
    analytics_enabled: bool = Field(True, description="Enable analytics tracking")
    analytics_tracking_id: Optional[str] = Field(None, description="Analytics tracking identifier")
    
    # Behavior
    auto_open: bool = Field(False, description="Auto-open chat on page load")
    auto_open_delay: int = Field(3000, description="Auto-open delay in milliseconds")
    persistent_menu: bool = Field(True, description="Show persistent menu options")
    
    # Content
    welcome_message: str = Field("Hello! How can I help you today?", description="Initial welcome message")
    placeholder_text: str = Field("Type your message...", description="Input placeholder text")
    
    # Branding
    brand_name: str = Field("Chronos AI", description="Brand name to display")
    brand_logo: Optional[str] = Field(None, description="Brand logo URL")
    
    # Advanced UI
    show_typing_indicator: bool = Field(True, description="Show typing indicator")
    show_message_timestamps: bool = Field(True, description="Show message timestamps")
    show_user_avatars: bool = Field(True, description="Show user avatars")
    
    # Media handling
    allow_file_uploads: bool = Field(True, description="Allow file uploads")
    allowed_file_types: List[str] = Field(["image/*", "application/pdf", "text/*"], description="Allowed file MIME types")
    max_file_size_mb: int = Field(10, description="Maximum file size in MB")


class WebChatMessage(BaseModel):
    message_id: str
    content: str
    sender: str  # "user" or "bot"
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
    
    # Message type
    message_type: str = Field("text", description="Message type: text, image, file, audio, system")
    
    # Media handling
    media_url: Optional[str] = Field(None, description="Media URL")
    media_type: Optional[str] = Field(None, description="Media MIME type")
    file_name: Optional[str] = Field(None, description="File name")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    
    # Status tracking
    status: str = Field("sent", description="Message status: sent, delivered, read, failed")
    
    # Analytics
    analytics_id: Optional[str] = Field(None, description="Analytics tracking ID")
    
    # Voice message
    voice_transcript: Optional[str] = Field(None, description="Transcript for voice messages")
    voice_duration: Optional[float] = Field(None, description="Voice message duration in seconds")
    
    # Feedback
    user_feedback: Optional[Dict[str, Any]] = Field(None, description="User feedback on message")
    
    # Read receipts
    read_at: Optional[str] = Field(None, description="When message was read")
    delivered_at: Optional[str] = Field(None, description="When message was delivered")

class WebChatSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    agent_id: Optional[int] = None
    messages: List[WebChatMessage] = []
    status: str = "active"  # active, ended, archived
    created_at: str
    updated_at: str
    
    # Session metadata
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="User IP address")
    device_type: Optional[str] = Field(None, description="Device type: mobile, desktop, tablet")
    
    # Analytics
    analytics_enabled: bool = Field(True, description="Enable session analytics")
    session_duration: Optional[float] = Field(None, description="Session duration in seconds")
    
    # User information
    user_name: Optional[str] = Field(None, description="User name")
    user_email: Optional[str] = Field(None, description="User email")
    user_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional user metadata")
    
    # Context
    current_context: Optional[Dict[str, Any]] = Field(None, description="Current conversation context")
    conversation_history: List[Dict[str, Any]] = Field([], description="Conversation history")
    
    # Preferences
    user_preferences: Dict[str, Any] = Field({}, description="User preferences for this session")
    
    # Feedback
    session_feedback: Optional[Dict[str, Any]] = Field(None, description="Session feedback")
    
    # Voice settings
    voice_settings: Dict[str, Any] = Field(
        {
            "enabled": False,
            "language": "en-US",
            "rate": 1.0,
            "pitch": 1.0
        },
        description="Voice settings for this session"
    )


class WebChatSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    agent_id: Optional[int] = None
    messages: List[WebChatMessage] = []
    status: str = "active"  # active, ended, archived
    created_at: str
    updated_at: str


class WebChatError(Exception):
    """Custom exception for WebChat errors"""
    pass


class WebChatManager:
    """
    WebChat Manager
    
    Handles WebChat sessions, embed configurations, and message routing.
    """

    def __init__(self):
        self.sessions: Dict[str, WebChatSession] = {}
        self.configs: Dict[str, WebChatConfig] = {}
        self.default_config: Optional[str] = None

    async def create_session(self, session_id: str, config: WebChatConfig, user_id: Optional[str] = None, agent_id: Optional[int] = None, **kwargs) -> WebChatSession:
        """Create a new WebChat session with advanced features"""
        from datetime import datetime
        
        session = WebChatSession(
            session_id=session_id,
            user_id=user_id,
            agent_id=agent_id,
            messages=[],
            status="active",
            created_at=self._get_current_timestamp(),
            updated_at=self._get_current_timestamp(),
            user_agent=kwargs.get("user_agent"),
            ip_address=kwargs.get("ip_address"),
            device_type=kwargs.get("device_type"),
            user_name=kwargs.get("user_name"),
            user_email=kwargs.get("user_email"),
            user_metadata=kwargs.get("user_metadata"),
            analytics_enabled=config.analytics_enabled,
            voice_settings={
                "enabled": config.voice_input_enabled or config.voice_output_enabled,
                "language": config.voice_language,
                "rate": config.voice_rate,
                "pitch": config.voice_pitch
            }
        )
        
        self.sessions[session_id] = session
        
        # Store config if it's a new one
        config_id = f"config_{session_id}"
        self.configs[config_id] = config
        
        if not self.default_config:
            self.default_config = config_id
        
        # Send welcome message if configured
        if config.welcome_message:
            welcome_message = WebChatMessage(
                message_id=f"welcome_{datetime.now().timestamp()}",
                content=config.welcome_message,
                sender="bot",
                timestamp=self._get_current_timestamp(),
                message_type="text",
                status="delivered"
            )
            session.messages.append(welcome_message)
        
        logger.info(f"Created WebChat session {session_id} for user {user_id}")
        
        return session

    async def get_session(self, session_id: str) -> WebChatSession:
        """Get a WebChat session"""
        if session_id not in self.sessions:
            raise WebChatError(f"WebChat session {session_id} not found")
        
        return self.sessions[session_id]

    async def send_message(self, session_id: str, message: WebChatMessage) -> WebChatMessage:
        """Send a message in a WebChat session with advanced features"""
        if session_id not in self.sessions:
            raise WebChatError(f"WebChat session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Add timestamp if not provided
        if not message.timestamp:
            message.timestamp = self._get_current_timestamp()
        
        # Generate analytics ID if not provided
        if not message.analytics_id:
            import uuid
            message.analytics_id = str(uuid.uuid4())
        
        # Set default status
        if not message.status:
            message.status = "sent"
        
        # Handle voice messages
        if message.message_type == "audio" and message.media_url:
            # In a real implementation, this would transcribe the voice message
            # For now, we'll simulate it
            message.voice_transcript = f"Transcript: {message.content[:100]}..." if len(message.content) > 100 else f"Transcript: {message.content}"
            message.voice_duration = 15.5  # Simulated duration
        
        session.messages.append(message)
        session.updated_at = self._get_current_timestamp()
        
        # Update conversation history
        session.conversation_history.append({
            "timestamp": message.timestamp,
            "sender": message.sender,
            "content": message.content,
            "message_type": message.message_type
        })
        
        # Track analytics if enabled
        if session.analytics_enabled:
            await self._track_webchat_analytics(session_id, message)
        
        logger.debug(f"Message {message.message_id} added to session {session_id}")
        
        return message
    
    async def _track_webchat_analytics(self, session_id: str, message: WebChatMessage):
        """Track WebChat message analytics"""
        from datetime import datetime
        
        session = self.sessions[session_id]
        
        # Update session duration
        if session.created_at:
            session.session_duration = (datetime.now() - datetime.fromisoformat(session.created_at)).total_seconds()
        
        # In a real implementation, this would integrate with analytics services
        # For now, we'll just log the analytics data
        analytics_data = {
            "session_id": session_id,
            "message_id": message.message_id,
            "analytics_id": message.analytics_id,
            "user_id": session.user_id,
            "agent_id": session.agent_id,
            "timestamp": message.timestamp,
            "message_type": message.message_type,
            "content_length": len(message.content),
            "sender": message.sender,
            "status": message.status,
            "session_duration": session.session_duration
        }
        
        logger.info(f"WebChat Analytics: {analytics_data}")
        
        # If analytics tracking ID is configured, send to analytics service
        config = await self.get_config()
        if config.analytics_enabled and config.analytics_tracking_id:
            # In a real implementation, this would send to Google Analytics, Mixpanel, etc.
            logger.info(f"Sending analytics to tracking ID {config.analytics_tracking_id}")

    async def get_messages(self, session_id: str, limit: int = 50) -> List[WebChatMessage]:
        """Get messages from a WebChat session"""
        if session_id not in self.sessions:
            raise WebChatError(f"WebChat session {session_id} not found")
        
        session = self.sessions[session_id]
        return session.messages[-limit:]

    async def end_session(self, session_id: str) -> WebChatSession:
        """End a WebChat session"""
        if session_id not in self.sessions:
            raise WebChatError(f"WebChat session {session_id} not found")
        
        session = self.sessions[session_id]
        session.status = "ended"
        session.updated_at = self._get_current_timestamp()
        
        return session

    async def archive_session(self, session_id: str) -> WebChatSession:
        """Archive a WebChat session"""
        if session_id not in self.sessions:
            raise WebChatError(f"WebChat session {session_id} not found")
        
        session = self.sessions[session_id]
        session.status = "archived"
        session.updated_at = self._get_current_timestamp()
        
        return session

    async def get_config(self, config_id: Optional[str] = None) -> WebChatConfig:
        """Get a WebChat configuration"""
        if not config_id:
            if not self.default_config:
                raise WebChatError("No default WebChat configuration available")
            return self.configs[self.default_config]
        
        if config_id not in self.configs:
            raise WebChatError(f"WebChat configuration {config_id} not found")
        
        return self.configs[config_id]

    async def update_config(self, config_id: str, config: WebChatConfig) -> WebChatConfig:
        """Update a WebChat configuration"""
        if config_id not in self.configs:
            raise WebChatError(f"WebChat configuration {config_id} not found")
        
        self.configs[config_id] = config
        return config

    async def generate_embed_code(self, session_id: str, config_id: Optional[str] = None) -> str:
        """Generate embed code for WebChat"""
        session = await self.get_session(session_id)
        config = await self.get_config(config_id)
        
        if config.embed_type == "bubble":
            return self._generate_bubble_embed(session, config)
        elif config.embed_type == "iframe":
            return self._generate_iframe_embed(session, config)
        elif config.embed_type == "standalone":
            return self._generate_standalone_embed(session, config)
        elif config.embed_type == "react":
            return self._generate_react_embed(session, config)
        else:
            raise WebChatError(f"Unknown embed type: {config.embed_type}")

    def _generate_bubble_embed(self, session: WebChatSession, config: WebChatConfig) -> str:
        """Generate bubble embed code with advanced features"""
        theme_css = self._generate_theme_css(config.theme)
        accessibility_css = self._generate_accessibility_css(config.accessibility_features)
        
        # Generate unique IDs for elements
        bubble_id = f"chronos-webchat-bubble-{session.session_id}"
        window_id = f"chronos-chat-window-{session.session_id}"
        messages_id = f"chronos-chat-messages-{session.session_id}"
        input_id = f"chronos-chat-input-{session.session_id}"
        
        # Voice input/output configuration
        voice_input_button = ""
        voice_output_button = ""
        
        if config.voice_input_enabled:
            voice_input_button = f'''
                <button id="{bubble_id}-voice-input"
                        style="background: none; border: none; color: {config.theme.primary_color}; cursor: pointer; margin-left: 8px;"
                        onclick="toggleVoiceInput()"
                        title="Voice Input">
                    🎤
                </button>
            '''
        
        if config.voice_output_enabled:
            voice_output_button = f'''
                <button id="{bubble_id}-voice-output"
                        style="background: none; border: none; color: {config.theme.primary_color}; cursor: pointer; margin-left: 4px;"
                        onclick="toggleVoiceOutput()"
                        title="Voice Output">
                    🔊
                </button>
            '''
        
        # Feedback button
        feedback_button = ""
        if config.feedback_enabled:
            feedback_button = f'''
                <button id="{bubble_id}-feedback"
                        style="background: none; border: none; color: {config.theme.text_color}; cursor: pointer; margin-left: 8px;"
                        onclick="showFeedbackForm()"
                        title="Feedback">
                    ❤️
                </button>
            '''
        
        # File upload button
        file_upload_button = ""
        if config.allow_file_uploads:
            file_upload_button = f'''
                <label style="cursor: pointer; margin-left: 8px;">
                    <input type="file" id="{bubble_id}-file-upload"
                           style="display: none;"
                           accept="{','.join(config.allowed_file_types)}"
                           onchange="handleFileUpload()">
                    <span style="color: {config.theme.primary_color}; cursor: pointer;">📎</span>
                </label>
            '''
        
        embed_code = f'''
        <!-- Chronos AI WebChat Bubble Embed -->
        <div id="{bubble_id}" style="{theme_css}{accessibility_css}">
            <style>
                #{bubble_id} {{
                    position: fixed;
                    {self._get_position_style(config.position)};
                    z-index: 9999;
                }}
                 
                #{bubble_id} .bubble {{
                    width: 60px;
                    height: 60px;
                    background-color: {config.theme.primary_color};
                    color: {config.theme.text_color};
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    transition: transform 0.2s ease;
                }}
                 
                #{bubble_id} .bubble:hover {{
                    transform: scale(1.1);
                }}
                 
                #{bubble_id} .chat-window {{
                    position: fixed;
                    {self._get_position_style(config.position, offset=True)};
                    width: 350px;
                    height: 500px;
                    background-color: {config.theme.background_color};
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                    display: none;
                    flex-direction: column;
                    overflow: hidden;
                }}
                 
                #{bubble_id} .chat-header {{
                    background-color: {config.theme.primary_color};
                    color: {config.theme.text_color};
                    padding: 12px 16px;
                    font-weight: 600;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                 
                #{bubble_id} .chat-messages {{
                    flex: 1;
                    padding: 16px;
                    overflow-y: auto;
                    background-color: {config.theme.background_color};
                }}
                 
                #{bubble_id} .chat-input {{
                    padding: 12px;
                    border-top: 1px solid #e5e7eb;
                    background-color: {config.theme.background_color};
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                 
                #{bubble_id} .message {{
                    margin-bottom: 12px;
                    padding: 8px 12px;
                    border-radius: 8px;
                    max-width: 80%;
                    position: relative;
                }}
                 
                #{bubble_id} .message.user {{
                    background-color: {config.theme.primary_color};
                    color: {config.theme.text_color};
                    margin-left: auto;
                }}
                 
                #{bubble_id} .message.bot {{
                    background-color: #f3f4f6;
                    color: #111827;
                    margin-right: auto;
                }}
                 
                #{bubble_id} .message-timestamp {{
                    font-size: 10px;
                    color: #9ca3af;
                    margin-top: 2px;
                    text-align: right;
                }}
                 
                #{bubble_id} .typing-indicator {{
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    font-size: 12px;
                    color: #9ca3af;
                }}
                 
                #{bubble_id} .typing-dot {{
                    width: 6px;
                    height: 6px;
                    background-color: #9ca3af;
                    border-radius: 50%;
                    animation: typing 1.4s infinite ease-in-out;
                }}
                 
                #{bubble_id} .typing-dot:nth-child(1) {{ animation-delay: 0s; }}
                #{bubble_id} .typing-dot:nth-child(2) {{ animation-delay: 0.2s; }}
                #{bubble_id} .typing-dot:nth-child(3) {{ animation-delay: 0.4s; }}
                 
                @keyframes typing {{
                    0%, 60%, 100% {{ transform: translateY(0); }}
                    30% {{ transform: translateY(-4px); }}
                }}
                 
                #{bubble_id} .feedback-form {{
                    position: absolute;
                    bottom: 60px;
                    left: 0;
                    right: 0;
                    background-color: {config.theme.background_color};
                    padding: 12px;
                    border-top: 1px solid #e5e7eb;
                    display: none;
                    z-index: 10;
                }}
                 
                #{bubble_id} .feedback-form.show {{
                    display: block;
                }}
            </style>
             
            <div class="bubble" onclick="toggleChatWindow()">
                💬
            </div>
             
            <div class="chat-window" id="{window_id}">
                <div class="chat-header">
                    <span>{config.brand_name or 'Chronos AI Chat'}</span>
                    <div style="display: flex; align-items: center;">
                        {voice_output_button}
                        {feedback_button}
                        <button onclick="toggleChatWindow()" style="background: none; border: none; color: {config.theme.text_color}; cursor: pointer; margin-left: 4px;">✕</button>
                    </div>
                </div>
                <div class="chat-messages" id="{messages_id}">
                    <!-- Messages will be loaded here -->
                </div>
                <div class="chat-input">
                    {file_upload_button}
                    <input type="text" id="{input_id}" placeholder="{config.placeholder_text}"
                           style="flex: 1; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px;"
                           onkeypress="handleKeyPress(event)">
                    {voice_input_button}
                    <button onclick="sendMessage()"
                            style="background-color: {config.theme.primary_color}; color: {config.theme.text_color}; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer;">
                        →
                    </button>
                </div>
                
                <!-- Feedback Form -->
                <div class="feedback-form" id="{bubble_id}-feedback-form">
                    <p style="margin-bottom: 8px; font-size: 14px; font-weight: 500;">How was this response?</p>
                    <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                        <button onclick="submitFeedback('thumbs_up')" style="background: none; border: none; font-size: 20px; cursor: pointer;">👍</button>
                        <button onclick="submitFeedback('thumbs_down')" style="background: none; border: none; font-size: 20px; cursor: pointer;">👎</button>
                    </div>
                    <textarea id="{bubble_id}-feedback-text" placeholder="Additional comments..."
                              style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; margin-bottom: 8px; resize: vertical;"></textarea>
                    <div style="display: flex; gap: 8px;">
                        <button onclick="cancelFeedback()" style="flex: 1; padding: 6px 12px; background: none; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer;">Cancel</button>
                        <button onclick="submitFeedback('text')" style="flex: 1; padding: 6px 12px; background-color: {config.theme.primary_color}; color: {config.theme.text_color}; border: none; border-radius: 6px; cursor: pointer;">Submit</button>
                    </div>
                </div>
            </div>
             
            <script>
                let sessionId = '{session.session_id}';
                let webSocket = null;
                let isRecording = false;
                let recognition = null;
                let synth = window.speechSynthesis;
                let currentFeedbackMessage = null;
                
                // Auto-open if configured
                {f'setTimeout(toggleChatWindow, {config.auto_open_delay})' if config.auto_open else '// Auto-open disabled'}
                
                function toggleChatWindow() {{
                    const chatWindow = document.getElementById('{window_id}');
                    chatWindow.style.display = chatWindow.style.display === 'flex' ? 'none' : 'flex';
                    
                    if (chatWindow.style.display === 'flex') {{
                        loadMessages();
                        connectWebSocket();
                    }}
                }}
                
                function loadMessages() {{
                    fetch('/api/v1/webchat/messages/' + sessionId)
                        .then(response => response.json())
                        .then(messages => {{
                            const messagesContainer = document.getElementById('{messages_id}');
                            messagesContainer.innerHTML = '';
                            
                            messages.forEach(msg => {{
                                const messageElement = document.createElement('div');
                                messageElement.className = 'message ' + msg.sender;
                                messageElement.innerHTML = msg.content;
                                
                                // Add timestamp if enabled
                                {f'''if ({config.show_message_timestamps}) {{
                                    const timestampElement = document.createElement('div');
                                    timestampElement.className = 'message-timestamp';
                                    timestampElement.textContent = new Date(msg.timestamp).toLocaleTimeString();
                                    messageElement.appendChild(timestampElement);
                                }}''' if config.show_message_timestamps else ''}
                                
                                messagesContainer.appendChild(messageElement);
                            }});
                            
                            messagesContainer.scrollTop = messagesContainer.scrollHeight;
                        }});
                }}
                
                function connectWebSocket() {{
                    if (webSocket) return;
                    
                    webSocket = new WebSocket('ws://' + window.location.host + '/api/v1/webchat/ws/' + sessionId);
                    
                    webSocket.onmessage = function(event) {{
                        const message = JSON.parse(event.data);
                        const messagesContainer = document.getElementById('{messages_id}');
                        
                        const messageElement = document.createElement('div');
                        messageElement.className = 'message ' + message.sender;
                        messageElement.innerHTML = message.content;
                        
                        // Add timestamp if enabled
                        {f'''if ({config.show_message_timestamps}) {{
                            const timestampElement = document.createElement('div');
                            timestampElement.className = 'message-timestamp';
                            timestampElement.textContent = new Date(message.timestamp).toLocaleTimeString();
                            messageElement.appendChild(timestampElement);
                        }}''' if config.show_message_timestamps else ''}
                        
                        messagesContainer.appendChild(messageElement);
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                        
                        // Auto-read voice messages if enabled
                        {f'''if ({config.voice_output_enabled} && message.sender === 'bot') {{
                            setTimeout(() => speakMessage(message.content), 1000);
                        }}''' if config.voice_output_enabled else ''}
                    }};
                    
                    webSocket.onclose = function() {{
                        webSocket = null;
                        setTimeout(connectWebSocket, 5000);
                    }};
                }}
                
                function handleKeyPress(event) {{
                    if (event.key === 'Enter') {{
                        sendMessage();
                    }}
                }}
                
                function sendMessage() {{
                    const input = document.getElementById('{input_id}');
                    const content = input.value.trim();
                    
                    if (!content) return;
                    
                    const message = {{
                        message_id: 'msg-' + Date.now(),
                        content: content,
                        sender: 'user',
                        timestamp: new Date().toISOString(),
                        message_type: 'text'
                    }};
                    
                    // Add to UI immediately
                    const messagesContainer = document.getElementById('{messages_id}');
                    const messageElement = document.createElement('div');
                    messageElement.className = 'message user';
                    messageElement.innerHTML = content;
                    
                    // Add timestamp if enabled
                    {f'''if ({config.show_message_timestamps}) {{
                        const timestampElement = document.createElement('div');
                        timestampElement.className = 'message-timestamp';
                        timestampElement.textContent = new Date().toLocaleTimeString();
                        messageElement.appendChild(timestampElement);
                    }}''' if config.show_message_timestamps else ''}
                    
                    messagesContainer.appendChild(messageElement);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    
                    // Send to server
                    fetch('/api/v1/webchat/messages/' + sessionId, {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify(message)
                    }});
                    
                    input.value = '';
                }}
                
                // Voice Input Functions
                {f'''function toggleVoiceInput() {{
                    const input = document.getElementById('{input_id}');
                    
                    if (!isRecording) {{
                        startVoiceInput();
                    }} else {{
                        stopVoiceInput();
                    }}
                }}
                
                function startVoiceInput() {{
                    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                        alert('Voice input not supported in your browser');
                        return;
                    }}
                    
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.lang = '{config.voice_language}';
                    recognition.interimResults = true;
                    
                    recognition.onresult = function(event) {{
                        const transcript = event.results[0][0].transcript;
                        document.getElementById('{input_id}').value = transcript;
                    }};
                    
                    recognition.onerror = function(event) {{
                        console.error('Voice recognition error:', event.error);
                        stopVoiceInput();
                    }};
                    
                    recognition.onend = function() {{
                        stopVoiceInput();
                    }};
                    
                    recognition.start();
                    isRecording = true;
                    document.getElementById('{bubble_id}-voice-input').textContent = '⏹️';
                }}
                
                function stopVoiceInput() {{
                    if (recognition) {{
                        recognition.stop();
                    }}
                    isRecording = false;
                    document.getElementById('{bubble_id}-voice-input').textContent = '🎤';
                }}''' if config.voice_input_enabled else '// Voice input disabled'}
                
                // Voice Output Functions
                {f'''function toggleVoiceOutput() {{
                    const button = document.getElementById('{bubble_id}-voice-output');
                    const isEnabled = button.textContent === '🔊';
                    button.textContent = isEnabled ? '🔇' : '🔊';
                    
                    // In a real implementation, this would toggle voice output globally
                    console.log('Voice output ' + (isEnabled ? 'enabled' : 'disabled'));
                }}
                
                function speakMessage(text) {{
                    if (!synth) return;
                    
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = '{config.voice_language}';
                    utterance.rate = {config.voice_rate};
                    utterance.pitch = {config.voice_pitch};
                    
                    synth.speak(utterance);
                }}''' if config.voice_output_enabled else '// Voice output disabled'}
                
                // File Upload Functions
                {f'''function handleFileUpload() {{
                    const fileInput = document.getElementById('{bubble_id}-file-upload');
                    const file = fileInput.files[0];
                    
                    if (!file) return;
                    
                    // Check file size
                    if (file.size > {config.max_file_size_mb * 1024 * 1024}) {{
                        alert('File size exceeds {config.max_file_size_mb}MB limit');
                        return;
                    }}
                    
                    // Check file type
                    const allowedTypes = {config.allowed_file_types};
                    const fileTypeMatch = allowedTypes.some(type =>
                        file.type.match(new RegExp(type.replace('*', '.*')))
                    );
                    
                    if (!fileTypeMatch) {{
                        alert('File type not allowed');
                        return;
                    }}
                    
                    // Show uploading status
                    const messagesContainer = document.getElementById('{messages_id}');
                    const statusElement = document.createElement('div');
                    statusElement.className = 'message user';
                    statusElement.textContent = 'Uploading ' + file.name + '...';
                    messagesContainer.appendChild(statusElement);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    
                    // In a real implementation, this would upload the file
                    // For now, we'll simulate it
                    setTimeout(() => {{
                        statusElement.textContent = 'Uploaded ' + file.name;
                        
                        // Send file message
                        const fileMessage = {{
                            message_id: 'file-' + Date.now(),
                            content: file.name,
                            sender: 'user',
                            timestamp: new Date().toISOString(),
                            message_type: 'file',
                            file_name: file.name,
                            file_size: file.size,
                            media_type: file.type
                        }};
                        
                        fetch('/api/v1/webchat/messages/' + sessionId, {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }},
                            body: JSON.stringify(fileMessage)
                        }});
                    }}, 2000);
                    
                    // Reset file input
                    fileInput.value = '';
                }}''' if config.allow_file_uploads else '// File uploads disabled'}
                
                // Feedback Functions
                {f'''function showFeedbackForm() {{
                    const feedbackForm = document.getElementById('{bubble_id}-feedback-form');
                    feedbackForm.classList.add('show');
                }}
                
                function cancelFeedback() {{
                    const feedbackForm = document.getElementById('{bubble_id}-feedback-form');
                    feedbackForm.classList.remove('show');
                    document.getElementById('{bubble_id}-feedback-text').value = '';
                    currentFeedbackMessage = null;
                }}
                
                function submitFeedback(type) {{
                    const feedbackText = document.getElementById('{bubble_id}-feedback-text').value;
                    
                    // In a real implementation, this would send feedback to the server
                    const feedbackData = {{
                        session_id: sessionId,
                        message_id: currentFeedbackMessage || 'general',
                        feedback_type: type,
                        feedback_text: feedbackText,
                        timestamp: new Date().toISOString()
                    }};
                    
                    console.log('Feedback submitted:', feedbackData);
                    
                    // Show thank you message
                    const messagesContainer = document.getElementById('{messages_id}');
                    const thankYouElement = document.createElement('div');
                    thankYouElement.className = 'message bot';
                    thankYouElement.textContent = 'Thank you for your feedback! 💙';
                    messagesContainer.appendChild(thankYouElement);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    
                    cancelFeedback();
                }}
                
                // Allow setting current feedback message
                function setFeedbackMessage(messageId) {{
                    currentFeedbackMessage = messageId;
                }}''' if config.feedback_enabled else '// Feedback disabled'}
            </script>
        </div>
        '''
         
        return embed_code

    def _generate_iframe_embed(self, session: WebChatSession, config: WebChatConfig) -> str:
        """Generate iframe embed code"""
        theme_params = '&'.join([f"theme[{k}]={v}" for k, v in config.theme.items()])
        
        embed_code = f'''
        <!-- Chronos AI WebChat Iframe Embed -->
        <iframe
            src="/webchat/iframe/{session.session_id}?{theme_params}"
            width="100%"
            height="600"
            frameborder="0"
            style="border: none; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);"
            allow="microphone; camera"
        ></iframe>
        '''
        
        return embed_code

    def _generate_standalone_embed(self, session: WebChatSession, config: WebChatConfig) -> str:
        """Generate standalone embed code"""
        embed_code = f'''
        <!-- Chronos AI WebChat Standalone Embed -->
        <div id="chronos-webchat-standalone" style="width: 100%; max-width: 800px; margin: 0 auto;">
            <iframe
                src="/webchat/standalone/{session.session_id}"
                width="100%"
                height="700"
                frameborder="0"
                style="border: none; border-radius: 12px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);"
                allow="microphone; camera"
            ></iframe>
        </div>
        '''
        
        return embed_code

    def _generate_react_embed(self, session: WebChatSession, config: WebChatConfig) -> str:
        """Generate React component embed code"""
        theme_json = json.dumps(config.theme)
        
        embed_code = '''
        // Chronos AI WebChat React Component
        import React, { useState, useEffect, useRef } from 'react';

        const ChronosWebChat = () => {
            const [messages, setMessages] = useState([]);
            const [inputValue, setInputValue] = useState('');
            const [isConnected, setIsConnected] = useState(false);
            const messagesEndRef = useRef(null);
            
            const sessionId = '%s';
            const theme = %s;
            
            useEffect(() => {
                // Load initial messages
                fetch('/api/v1/webchat/messages/' + sessionId)
                    .then(response => response.json())
                    .then(data => setMessages(data));
                
                // Scroll to bottom
                scrollToBottom();
            }, []);
            
            useEffect(() => {
                scrollToBottom();
            }, [messages]);
            
            const scrollToBottom = () => {
                messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            };
            
            const sendMessage = () => {
                if (!inputValue.trim()) return;
                
                const newMessage = {
                    message_id: 'msg-' + Date.now(),
                    content: inputValue,
                    sender: 'user',
                    timestamp: new Date().toISOString()
                };
                
                // Optimistic UI update
                setMessages([...messages, newMessage]);
                setInputValue('');
                
                // Send to server
                fetch('/api/v1/webchat/messages/' + sessionId, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(newMessage)
                });
            };
            
            const handleKeyPress = (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            };
            
            const handleInputChange = (e) => {
                setInputValue(e.target.value);
            };
            
            return (
                <div style={{
                    width: '100%',
                    maxWidth: '800px',
                    height: '600px',
                    display: 'flex',
                    flexDirection: 'column',
                    border: '1px solid #e5e7eb',
                    borderRadius: '12px',
                    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
                    overflow: 'hidden',
                    backgroundColor: theme.background_color
                }}>
                    <div style={{
                        backgroundColor: theme.primary_color,
                        color: theme.text_color,
                        padding: '12px 16px',
                        fontWeight: '600',
                        fontSize: '16px'
                    }}>
                        Chronos AI Chat
                    </div>
                    
                    <div style={{
                        flex: 1,
                        padding: '16px',
                        overflowY: 'auto',
                        backgroundColor: theme.background_color
                    }}>
                        {messages.map((msg) => (
                            <div
                                key={msg.message_id}
                                style={{
                                    marginBottom: '12px',
                                    padding: '8px 12px',
                                    borderRadius: '8px',
                                    maxWidth: '80%',
                                    marginLeft: msg.sender === 'user' ? 'auto' : '0',
                                    marginRight: msg.sender === 'bot' ? 'auto' : '0',
                                    backgroundColor: msg.sender === 'user' ? theme.primary_color : '#f3f4f6',
                                    color: msg.sender === 'user' ? theme.text_color : '#111827'
                                }}
                            >
                                {msg.content}
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                    
                    <div style={{
                        padding: '12px',
                        borderTop: '1px solid #e5e7eb',
                        backgroundColor: theme.background_color,
                        display: 'flex',
                        gap: '8px'
                    }}>
                        <input
                            type="text"
                            value={inputValue}
                            onChange={handleInputChange}
                            onKeyPress={handleKeyPress}
                            placeholder="Type your message..."
                            style={{
                                flex: 1,
                                padding: '8px 12px',
                                border: '1px solid #d1d5db',
                                borderRadius: '6px',
                                fontSize: '14px'
                            }}
                        />
                        <button
                            onClick={sendMessage}
                            style={{
                                padding: '8px 16px',
                                backgroundColor: theme.primary_color,
                                color: theme.text_color,
                                border: 'none',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '14px',
                                fontWeight: '500'
                            }}
                        >
                            Send
                        </button>
                    </div>
                </div>
            );
        };
        
        export default ChronosWebChat;
        ''' % (session.session_id, theme_json)
        
        return embed_code
    def _generate_theme_css(self, theme: Dict[str, Any]) -> str:
        """Generate CSS for theme"""
        return f'''
            --chronos-primary-color: {theme.primary_color};
            --chronos-secondary-color: {theme.secondary_color};
            --chronos-text-color: {theme.text_color};
            --chronos-bg-color: {theme.background_color};
        '''

    def _generate_accessibility_css(self, accessibility: Dict[str, bool]) -> str:
        """Generate CSS for accessibility features"""
        css = ""
        
        if accessibility.high_contrast:
            css += "--chronos-contrast: 2;"
        
        return css

    def _get_position_style(self, position: str, offset: bool = False) -> str:
        """Get CSS position style"""
        positions = {
            "bottom_right": {
                "bottom": "20px",
                "right": "20px"
            },
            "bottom_left": {
                "bottom": "20px",
                "left": "20px"
            },
            "top_right": {
                "top": "20px",
                "right": "20px"
            },
            "top_left": {
                "top": "20px",
                "left": "20px"
            }
        }
        
        if offset:
            # Add offset for chat window
            pos = positions.get(position, positions["bottom_right"])
            if "bottom" in pos:
                pos["bottom"] = "80px"
            elif "top" in pos:
                pos["top"] = "80px"
            if "right" in pos:
                pos["right"] = "80px"
            elif "left" in pos:
                pos["left"] = "80px"
            return '; '.join([f"{k}: {v}" for k, v in pos.items()])
        
        pos = positions.get(position, positions["bottom_right"])
        return '; '.join([f"{k}: {v}" for k, v in pos.items()])

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()


# Global WebChat manager instance
webchat_manager = WebChatManager()


async def initialize_webchat():
    """Initialize WebChat system"""
    logger.info("WebChat system initialized")


async def get_webchat_manager() -> WebChatManager:
    """Get the WebChat manager"""
    return webchat_manager
