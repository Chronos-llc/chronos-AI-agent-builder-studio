from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: AgentStatus = AgentStatus.DRAFT
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentCreate(AgentBase):
    model_config: Optional[Dict[str, Any]] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    model_config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(AgentBase):
    id: int
    model_config: Optional[Dict[str, Any]] = None
    usage_count: int
    success_rate: float
    avg_response_time: float
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentVersionBase(BaseModel):
    version_number: str
    changelog: Optional[str] = None
    is_current: bool = False


class AgentVersionCreate(AgentVersionBase):
    config_snapshot: Dict[str, Any]


class AgentVersionResponse(AgentVersionBase):
    id: int
    config_snapshot: Dict[str, Any]
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActionBase(BaseModel):
    name: str
    description: Optional[str] = None
    action_type: str


class ActionCreate(ActionBase):
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None


class ActionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    action_type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None


class ActionResponse(ActionBase):
    id: int
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Sub-Agent Configuration Schemas
class SummaryAgentConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable Summary Agent")
    summary_max_tokens: int = Field(default=100, description="Maximum tokens for summary generation")
    transcript_max_lines: int = Field(default=10, description="Maximum lines in transcript")
    model: str = Field(default="gpt-3.5-turbo", description="Model for summary generation")
    exposed_variables: Dict[str, str] = Field(
        default={
            "conversation.summaryagent.summary": "{{conversation.summaryagent.summary}}",
            "conversation.SummaryAgent.transcript": "{{conversation.SummaryAgent.transcript}}"
        },
        description="Exposed variables for templates"
    )


class TranslatorAgentConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable Translator Agent")
    detect_initial_language: bool = Field(default=True, description="Detect initial user language")
    detect_language_change: bool = Field(default=True, description="Detect language changes during conversation")
    model: str = Field(default="gpt-3.5-turbo", description="Model for translation")
    exposed_variables: Dict[str, str] = Field(
        default={
            "User.TranslatorAgent.Language": "{{User.TranslatorAgent.Language}}",
            "turn.TranslatorAgent.originalMessages": "{{turn.TranslatorAgent.originalMessages}}"
        },
        description="Exposed variables for templates"
    )


class KnowledgeAgentConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable Knowledge Agent")
    answer_manually: bool = Field(default=False, description="Allow manual answers")
    additional_context: bool = Field(default=True, description="Use additional context")
    model_strategy: str = Field(default="Hybrid", description="Model strategy (Fastest, Hybrid, Best)")
    fastest_model: str = Field(default="gpt-3.5-turbo", description="Model for fastest strategy")
    best_model: str = Field(default="gpt-4", description="Model for best strategy")
    question_extractor_model: str = Field(default="gpt-3.5-turbo", description="Model for question extraction")
    chunks_count: float = Field(default=20.00, description="Number of chunks for knowledge retrieval")
    exposed_variables: Dict[str, str] = Field(
        default={
            "turn.KnowledgeAgent.answer": "{{turn.KnowledgeAgent.answer}}",
            "turn.KnowledgeAgent.citations": "{{turn.KnowledgeAgent.citations}}"
        },
        description="Exposed variables for templates"
    )


class VisionAgentConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable Vision Agent")
    extract_from_incoming_images: bool = Field(default=True, description="Extract content from incoming images")
    exposed_variables: Dict[str, str] = Field(
        default={
            "turn.VisionAgent.content": "{{turn.VisionAgent.content}}"
        },
        description="Exposed variables for templates"
    )


class ImageGenerationAgentConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable Image Generation Agent")
    generate_image: bool = Field(default=True, description="Generate images")
    edit_images: bool = Field(default=False, description="Edit existing images")
    exposed_variables: Dict[str, str] = Field(
        default={
            "Turn.ImageGenerationAgent.content": "{{Turn.ImageGenerationAgent.content}}"
        },
        description="Exposed variables for templates"
    )


class VideoAgentConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable Video Agent")
    generate_video: bool = Field(default=False, description="Generate videos")
    analyze_incoming_videos: bool = Field(default=True, description="Analyze incoming videos")
    exposed_variables: Dict[str, str] = Field(
        default={
            "turn.VideoAgent.content": "{{turn.VideoAgent.content}}"
        },
        description="Exposed variables for templates"
    )


class PersonalityAgentConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable Personality Agent")
    personality_traits: Dict[str, float] = Field(
        default={
            "friendliness": 0.8,
            "professionalism": 0.7,
            "humor": 0.3,
            "formality": 0.5
        },
        description="Personality traits configuration"
    )
    tone_style: str = Field(default="balanced", description="Overall tone style")


class PolicyAgentConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable Policy Agent")
    compliance_rules: List[str] = Field(
        default=[
            "No personal data collection",
            "No offensive content",
            "No medical advice",
            "No legal advice"
        ],
        description="Compliance rules for agent behavior"
    )
    content_filters: List[str] = Field(
        default=[
            "hate speech",
            "violence",
            "adult content",
            "spam"
        ],
        description="Content filters to apply"
    )


class SubAgentConfig(BaseModel):
    summary_agent: SummaryAgentConfig = SummaryAgentConfig()
    translator_agent: TranslatorAgentConfig = TranslatorAgentConfig()
    knowledge_agent: KnowledgeAgentConfig = KnowledgeAgentConfig()
    vision_agent: VisionAgentConfig = VisionAgentConfig()
    image_generation_agent: ImageGenerationAgentConfig = ImageGenerationAgentConfig()
    video_agent: VideoAgentConfig = VideoAgentConfig()
    personality_agent: PersonalityAgentConfig = PersonalityAgentConfig()
    policy_agent: PolicyAgentConfig = PolicyAgentConfig()


class AgentConfigUpdate(BaseModel):
    sub_agent_config: Optional[SubAgentConfig] = None