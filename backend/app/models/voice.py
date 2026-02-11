from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base


class VoiceProvider(str, Enum):
    """Supported voice service providers"""
    OPENAI = "OPENAI"  # OpenAI Whisper (STT) and TTS
    ELEVENLABS = "ELEVENLABS"  # ElevenLabs TTS
    CARTESIA = "CARTESIA"  # Cartesia STT/TTS
    GOOGLE = "GOOGLE"  # Google Cloud Speech-to-Text and Text-to-Speech
    AZURE = "AZURE"  # Azure Cognitive Services
    AWS = "AWS"  # Amazon Polly and Transcribe
    DEEPGRAM = "DEEPGRAM"  # Deepgram STT
    ASSEMBLYAI = "ASSEMBLYAI"  # AssemblyAI STT


class VoiceGender(str, Enum):
    """Voice gender options"""
    MALE = "MALE"
    FEMALE = "FEMALE"
    NEUTRAL = "NEUTRAL"


class AudioFormat(str, Enum):
    """Supported audio formats"""
    MP3 = "MP3"
    WAV = "WAV"
    OGG = "OGG"
    WEBM = "WEBM"
    FLAC = "FLAC"


class VoiceConfiguration(Base):
    """Voice configuration for agents"""
    __tablename__ = "voice_configurations"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Voice enabled flag
    voice_enabled = Column(Boolean, default=False)
    
    # STT (Speech-to-Text) Configuration
    stt_provider = Column(SQLEnum(VoiceProvider), default=VoiceProvider.OPENAI)
    stt_model = Column(String(100), nullable=True)  # e.g., "whisper-1", "nova-2"
    stt_language = Column(String(10), default="en")  # ISO language code
    stt_config = Column(JSON, nullable=True)  # Provider-specific configuration
    
    # TTS (Text-to-Speech) Configuration
    tts_provider = Column(SQLEnum(VoiceProvider), default=VoiceProvider.OPENAI)
    tts_model = Column(String(100), nullable=True)  # e.g., "tts-1", "eleven_multilingual_v2"
    tts_voice = Column(String(100), nullable=True)  # Voice ID or name
    tts_voice_gender = Column(SQLEnum(VoiceGender), default=VoiceGender.NEUTRAL)
    tts_speed = Column(Float, default=1.0)  # Speech speed multiplier (0.5 - 2.0)
    tts_pitch = Column(Float, default=1.0)  # Voice pitch (0.5 - 2.0)
    tts_config = Column(JSON, nullable=True)  # Provider-specific configuration
    
    # Audio Settings
    audio_format = Column(SQLEnum(AudioFormat), default=AudioFormat.MP3)
    sample_rate = Column(Integer, default=24000)  # Hz
    bit_rate = Column(Integer, default=128)  # kbps
    
    # Advanced Features
    noise_reduction = Column(Boolean, default=True)
    echo_cancellation = Column(Boolean, default=True)
    auto_gain_control = Column(Boolean, default=True)
    voice_activity_detection = Column(Boolean, default=True)
    
    # Interruption handling
    allow_interruption = Column(Boolean, default=True)
    interruption_threshold = Column(Float, default=0.5)  # Confidence threshold
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="voice_configuration")
    user = relationship("User")
    sessions = relationship("VoiceSession", back_populates="configuration", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_voice_config_agent', 'agent_id'),
        Index('idx_voice_config_user', 'user_id'),
    )


class VoiceSession(Base):
    """Voice interaction sessions"""
    __tablename__ = "voice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey("voice_configurations.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    
    # Session identification
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    conversation_id = Column(String(255), nullable=True)  # Link to conversation context
    channel = Column(String(100), nullable=True)  # webchat, telegram, etc.
    user_identifier = Column(String(255), nullable=True)
    
    # Session state
    is_active = Column(Boolean, default=True)
    is_recording = Column(Boolean, default=False)
    
    # Session metadata
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    
    # Statistics
    total_audio_duration = Column(Float, default=0.0)  # Total audio processed (seconds)
    stt_requests = Column(Integer, default=0)
    tts_requests = Column(Integer, default=0)
    interruptions = Column(Integer, default=0)
    
    # Quality metrics
    avg_latency_ms = Column(Float, nullable=True)  # Average response latency
    avg_confidence = Column(Float, nullable=True)  # Average STT confidence
    error_count = Column(Integer, default=0)
    
    # Session data
    session_data = Column(JSON, nullable=True)  # Additional session information
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    configuration = relationship("VoiceConfiguration", back_populates="sessions")
    agent = relationship("Agent", back_populates="voice_sessions")
    interactions = relationship("VoiceInteraction", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_voice_session_agent', 'agent_id', 'is_active'),
        Index('idx_voice_session_created', 'created_at'),
    )


class VoiceInteraction(Base):
    """Individual voice interactions within a session"""
    __tablename__ = "voice_interactions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("voice_sessions.id", ondelete="CASCADE"), nullable=False)
    
    # Interaction type
    interaction_type = Column(String(20), nullable=False)  # "stt", "tts", "error"
    
    # Input/Output
    input_text = Column(Text, nullable=True)  # For TTS
    output_text = Column(Text, nullable=True)  # For STT
    audio_url = Column(String(500), nullable=True)  # URL to audio file
    audio_duration = Column(Float, nullable=True)  # Duration in seconds
    
    # Quality metrics
    confidence_score = Column(Float, nullable=True)  # STT confidence
    latency_ms = Column(Integer, nullable=True)  # Processing latency
    
    # Provider info
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    additional_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("VoiceSession", back_populates="interactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_voice_interaction_session', 'session_id', 'created_at'),
        Index('idx_voice_interaction_type', 'interaction_type'),
    )
