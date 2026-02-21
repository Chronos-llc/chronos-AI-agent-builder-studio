from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.schemas.phone_number import PhoneNumberProvider


class VoiceProvider(str, Enum):
    """Supported voice service providers"""
    OPENAI = "OPENAI"
    ELEVENLABS = "ELEVENLABS"
    CARTESIA = "CARTESIA"
    GOOGLE = "GOOGLE"
    AZURE = "AZURE"
    AWS = "AWS"
    DEEPGRAM = "DEEPGRAM"
    ASSEMBLYAI = "ASSEMBLYAI"


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


# Voice Configuration Schemas
class VoiceConfigurationCreate(BaseModel):
    """Schema for creating voice configuration"""
    voice_enabled: bool = Field(default=True, description="Enable voice features")
    
    # STT Configuration
    stt_provider: VoiceProvider = Field(default=VoiceProvider.OPENAI)
    stt_model: Optional[str] = Field(None, max_length=100)
    stt_language: str = Field(default="en", max_length=10)
    stt_config: Optional[Dict[str, Any]] = None
    
    # TTS Configuration
    tts_provider: VoiceProvider = Field(default=VoiceProvider.OPENAI)
    tts_model: Optional[str] = Field(None, max_length=100)
    tts_voice: Optional[str] = Field(None, max_length=100)
    tts_voice_gender: VoiceGender = Field(default=VoiceGender.NEUTRAL)
    tts_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    tts_pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    tts_config: Optional[Dict[str, Any]] = None
    
    # Audio Settings
    audio_format: AudioFormat = Field(default=AudioFormat.MP3)
    sample_rate: int = Field(default=24000, ge=8000, le=48000)
    bit_rate: int = Field(default=128, ge=64, le=320)
    
    # Advanced Features
    noise_reduction: bool = Field(default=True)
    echo_cancellation: bool = Field(default=True)
    auto_gain_control: bool = Field(default=True)
    voice_activity_detection: bool = Field(default=True)
    
    # Interruption handling
    allow_interruption: bool = Field(default=True)
    interruption_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

    # Telephony
    selected_phone_number_id: Optional[int] = None
    phone_provider_preference: Optional[PhoneNumberProvider] = None


class VoiceConfigurationUpdate(BaseModel):
    """Schema for updating voice configuration"""
    voice_enabled: Optional[bool] = None
    stt_provider: Optional[VoiceProvider] = None
    stt_model: Optional[str] = Field(None, max_length=100)
    stt_language: Optional[str] = Field(None, max_length=10)
    stt_config: Optional[Dict[str, Any]] = None
    tts_provider: Optional[VoiceProvider] = None
    tts_model: Optional[str] = Field(None, max_length=100)
    tts_voice: Optional[str] = Field(None, max_length=100)
    tts_voice_gender: Optional[VoiceGender] = None
    tts_speed: Optional[float] = Field(None, ge=0.5, le=2.0)
    tts_pitch: Optional[float] = Field(None, ge=0.5, le=2.0)
    tts_config: Optional[Dict[str, Any]] = None
    audio_format: Optional[AudioFormat] = None
    sample_rate: Optional[int] = Field(None, ge=8000, le=48000)
    bit_rate: Optional[int] = Field(None, ge=64, le=320)
    noise_reduction: Optional[bool] = None
    echo_cancellation: Optional[bool] = None
    auto_gain_control: Optional[bool] = None
    voice_activity_detection: Optional[bool] = None
    allow_interruption: Optional[bool] = None
    interruption_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    selected_phone_number_id: Optional[int] = None
    phone_provider_preference: Optional[PhoneNumberProvider] = None


class VoiceConfigurationResponse(BaseModel):
    """Response schema for voice configuration"""
    id: int
    agent_id: int
    user_id: int
    voice_enabled: bool
    stt_provider: VoiceProvider
    stt_model: Optional[str]
    stt_language: str
    stt_config: Optional[Dict[str, Any]]
    tts_provider: VoiceProvider
    tts_model: Optional[str]
    tts_voice: Optional[str]
    tts_voice_gender: VoiceGender
    tts_speed: float
    tts_pitch: float
    tts_config: Optional[Dict[str, Any]]
    audio_format: AudioFormat
    sample_rate: int
    bit_rate: int
    noise_reduction: bool
    echo_cancellation: bool
    auto_gain_control: bool
    voice_activity_detection: bool
    allow_interruption: bool
    interruption_threshold: float
    selected_phone_number_id: Optional[int]
    phone_provider_preference: Optional[PhoneNumberProvider]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Voice Session Schemas
class VoiceSessionCreate(BaseModel):
    """Schema for creating a voice session"""
    conversation_id: Optional[str] = Field(None, max_length=255)
    channel: Optional[str] = Field(None, max_length=100)
    user_identifier: Optional[str] = Field(None, max_length=255)
    session_data: Optional[Dict[str, Any]] = None


class VoiceSessionUpdate(BaseModel):
    """Schema for updating a voice session"""
    is_active: Optional[bool] = None
    is_recording: Optional[bool] = None
    session_data: Optional[Dict[str, Any]] = None


class VoiceSessionResponse(BaseModel):
    """Response schema for voice session"""
    id: int
    configuration_id: int
    agent_id: int
    session_id: str
    conversation_id: Optional[str]
    channel: Optional[str]
    user_identifier: Optional[str]
    is_active: bool
    is_recording: bool
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: int
    total_audio_duration: float
    stt_requests: int
    tts_requests: int
    interruptions: int
    avg_latency_ms: Optional[float]
    avg_confidence: Optional[float]
    error_count: int
    session_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# STT/TTS Operation Schemas
class STTRequest(BaseModel):
    """Schema for Speech-to-Text request"""
    audio_data: str = Field(..., description="Base64 encoded audio data or URL")
    audio_format: Optional[AudioFormat] = None
    language: Optional[str] = Field(None, max_length=10)
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")


class STTResponse(BaseModel):
    """Response schema for Speech-to-Text"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    language: Optional[str] = None
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    latency_ms: int = Field(..., description="Processing latency")
    provider: str
    model: Optional[str] = None


class TTSRequest(BaseModel):
    """Schema for Text-to-Speech request"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    voice: Optional[str] = Field(None, description="Voice ID or name")
    speed: Optional[float] = Field(None, ge=0.5, le=2.0)
    pitch: Optional[float] = Field(None, ge=0.5, le=2.0)
    audio_format: Optional[AudioFormat] = None
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")


class TTSResponse(BaseModel):
    """Response schema for Text-to-Speech"""
    audio_url: str = Field(..., description="URL to generated audio file")
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data")
    duration: float = Field(..., description="Audio duration in seconds")
    audio_format: AudioFormat
    latency_ms: int = Field(..., description="Processing latency")
    provider: str
    model: Optional[str] = None


# Voice Interaction Schemas
class VoiceInteractionResponse(BaseModel):
    """Response schema for voice interaction"""
    id: int
    session_id: int
    interaction_type: str
    input_text: Optional[str]
    output_text: Optional[str]
    audio_url: Optional[str]
    audio_duration: Optional[float]
    confidence_score: Optional[float]
    latency_ms: Optional[int]
    provider: Optional[str]
    model: Optional[str]
    error_message: Optional[str]
    retry_count: int
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Voice Analytics Schemas
class VoiceAnalytics(BaseModel):
    """Analytics for voice interactions"""
    total_sessions: int
    active_sessions: int
    total_stt_requests: int
    total_tts_requests: int
    total_audio_duration: float
    avg_session_duration: float
    avg_latency_ms: float
    avg_confidence: float
    total_errors: int
    error_rate: float
    by_provider: Dict[str, int] = Field(..., description="Usage by provider")
    by_channel: Dict[str, int] = Field(..., description="Usage by channel")


# Voice Testing Schemas
class VoiceTestRequest(BaseModel):
    """Schema for testing voice configuration"""
    test_text: str = Field(..., min_length=1, max_length=500, description="Text to test TTS")
    test_audio: Optional[str] = Field(None, description="Base64 audio to test STT")


class VoiceTestResponse(BaseModel):
    """Response schema for voice testing"""
    stt_result: Optional[STTResponse] = None
    tts_result: Optional[TTSResponse] = None
    success: bool
    errors: Optional[List[str]] = None
