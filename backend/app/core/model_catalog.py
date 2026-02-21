"""
Static model catalog and availability resolution for installed AI providers.
"""
from typing import Any, Dict, List, Set, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.integration import Integration as IntegrationModel
from app.models.integration import IntegrationConfig as IntegrationConfigModel


CAPABILITIES: Tuple[str, ...] = (
    "chat",
    "translation",
    "image",
    "video",
    "stt",
    "tts",
    "voice",
)

DEFAULT_CONTEXT_WINDOW = 16000

MODEL_CONTEXT_WINDOWS: Dict[str, int] = {
    "gpt-5.2": 400000,
    "gpt-5.1": 400000,
    "gpt-5": 400000,
    "gpt-5 mini": 128000,
    "gpt-5 nano": 64000,
    "gpt-5.1 codex": 128000,
    "gpt-5.1-codex-max": 256000,
    "gpt-5-codex": 128000,
    "gpt-5.2-pro": 400000,
    "gpt-5 pro": 400000,
    "gpt-4.1": 128000,
    "gpt-4.1 mini": 128000,
    "gpt-4.1 nano": 64000,
    "o4-mini": 128000,
    "gpt-4o": 128000,
    "gpt-4o mini": 128000,
    "gpt-4 turbo": 128000,
    "gpt-4": 8192,
    "o3": 200000,
    "o3-pro": 200000,
    "o3-mini": 200000,
    "o1": 200000,
    "o1-pro": 200000,
    "gpt-5.2-chat": 400000,
}


def get_context_window_for_model(model_name: str | None) -> int:
    if not model_name:
        return DEFAULT_CONTEXT_WINDOW

    normalized = model_name.strip().lower()
    if normalized in MODEL_CONTEXT_WINDOWS:
        return MODEL_CONTEXT_WINDOWS[normalized]

    # Heuristic fallback for third-party catalogs.
    if "nano" in normalized:
        return 64000
    if "mini" in normalized:
        return 128000
    if "think" in normalized or "reason" in normalized:
        return 200000
    if "gpt-5" in normalized or "o1" in normalized or "o3" in normalized:
        return 200000
    return DEFAULT_CONTEXT_WINDOW


def _dedupe(models: List[str]) -> List[str]:
    seen: Set[str] = set()
    deduped: List[str] = []
    for model in models:
        if model in seen:
            continue
        seen.add(model)
        deduped.append(model)
    return deduped


OPENAI_CHAT_MODELS = _dedupe(
    [
        "GPT-5.2",
        "GPT-5.1",
        "GPT-5",
        "GPT-5 mini",
        "GPT-5 nano",
        "GPT-5.1 codex",
        "GPT-5.1-codex-max",
        "GPT-5-codex",
        "GPT-5.2-pro",
        "GPT-5 pro",
        "GPT-4.1",
        "GPT-4.1 mini",
        "GPT-4.1 nano",
        "o4-mini",
        "GPT-4o",
        "GPT-4o mini",
        "GPT-4 turbo",
        "GPT-4",
        "o3",
        "o3-pro",
        "o1",
        "o3-mini",
        "o1-pro",
    ]
)


FIREWORKS_CHAT_MODELS = _dedupe(
    [
        "Minimax-M2.1",
        "Minimax-M2",
        "GLM-4.7",
        "GLM-4.6",
        "GLM-4.5",
        "Deepseek v3.2",
        "Kimi-K2-Thinking",
        "Kimi-K2-Instruct-0905",
        "Deepseek V3.1",
        "gpt-oss-120B",
        "gpt-oss-20B",
        "gpt-oss-safeguard-120B",
        "gpt-oss-safeguard-20B",
        "Qwen3-235B-A22B",
        "Qwen3-235B-A22B-Thinking-2507",
        "Qwen3-Coder-480B-A35B-Instruct",
        "Qwen3-235B-A22B-Instruct-2507",
        "Llama-3.3-70B-instruct",
        "Deepseek-R1-05/28",
        "Qwen3-Coder-30B-A3b-Instruct",
        "Deepseek-R1-Fast",
        "Cogito-671B-v2.1",
        "Deepseek-V3.1-Terminus",
        "Qwen3-8B",
        "Qwen3-30B-A3B",
        "Llama-4-Maverick-Instruct-(BASIC)",
        "Deepseek-V3-03-24",
        "Molmo2-8B",
        "Molmo2-4B",
        "Qwen3-Omni-30B-A3B-Instruct",
        "Gemma-3-12B-Instruct",
        "Gemma-3-4B-Instruct",
        "NVIDIA-Nemotron-Nano-3-30B-A3B",
        "Mistral-Large-3-675B-Instruct-2512",
        "Ministral-3-14B-Instruct-2512",
        "Ministral-3-8B-Instruct-2512",
        "Ministral-3-3B-Instruct-2512",
        "NVIDIA-Nemotron-Nano-9B-v2",
        "NVIDIA-Nemotron-Nano-12B-v2",
        "Qwen-3-Next-80B-A3B-Thinking",
        "Qwen-3-Next-80B-A3B-Instruct",
    ]
)


XAI_CHAT_MODELS = _dedupe(
    [
        "grok-4-1-fast-reasoning",
        "grok-4-1-fast-non-reasoning",
        "grok-4-fast-reasoning",
        "grok-4-fast-non-reasoning",
        "grok-code-fast-1",
        "grok-4-0709",
        "grok-3-mini",
        "grok-3",
    ]
)


OPENROUTER_CHAT_MODELS = _dedupe(
    [
        "Olmo-3.1-32B-instruct",
        "Mistral-small-creative",
        "Olmo-3.1-32B-Think",
        "MiMo-V2-Flash",
        "GPT-5.2-Chat",
        "Deepseek-V3-2-Speciale",
    ]
)

OPENAI_VIDEO_MODELS = _dedupe(
    [
        "sora",
        "sora-2",
        "sora-2-2025-12-08",
        "sora-2-2025-10-06",
        "sora-2pro",
    ]
)

OPENAI_IMAGE_MODELS = _dedupe(
    [
        "gpt-image-1",
        "gpt-image-1-mini",
        "gpt-image-1.5",
        "dall-e-3",
        "dall-e-2",
    ]
)

OPENAI_STT_MODELS = _dedupe(
    [
        "whisper-1",
        "gpt-4o-mini-transcribe",
        "gpt-4o-transcribe",
        "gpt-4o-transcribe-diarize",
    ]
)

OPENAI_TTS_MODELS = _dedupe(
    [
        "gpt-4o-mini-tts",
        "tts-1",
        "tts-1-hd",
    ]
)

OPENAI_VOICES = _dedupe(
    [
        "alloy",
        "ash",
        "ballad",
        "coral",
        "echo",
        "fable",
        "nova",
        "onyx",
        "sage",
        "shimmer",
        "verse",
        "marin",
        "cedar",
    ]
)

XAI_IMAGE_MODELS = _dedupe(
    [
        "grok-2-image-1212",
        "grok-imagine-image",
        "grok-imagine-image-pro",
    ]
)

XAI_VIDEO_MODELS = _dedupe(
    [
        "grok-imagine-video",
    ]
)

GOOGLE_IMAGE_MODELS = _dedupe(
    [
        "gemini-2.5-flash-image/nano-banana",
        "gemini-3-pro-image-preview/nano-banana-pro",
        "imagen-4.0-generate-001",
        "imagen-4.0-fast-generate-00",
        "imagen-4.0-ultra-generate-001",
        "imagen-3.0-capability-001",
        "imagen-3.0-generate-002",
        "imagen-3.0-generate-00",
        "virtual-try-on-001",
    ]
)

GOOGLE_VIDEO_MODELS = _dedupe(
    [
        "veo-2.0-generate-001",
        "veo-2.0-generate-exp",
        "veo-2.0-generate-preview",
        "veo-3.0-generate-001",
        "veo-3.0-fast-generate-001",
        "veo-3.0-generate-preview",
        "veo-3.0-fast-generate-preview",
        "veo-3.1-generate-001",
        "veo-3.1-fast-generate-001",
        "veo-3.1-generate-preview",
        "veo-3.1-fast-generate-preview",
    ]
)

FIREWORKS_STT_MODELS = _dedupe(
    [
        "Streaming-ASR-v1",
        "Streaming-ASR-v2",
        "Whisper-V3-Large",
        "Whisper-V3-Turbo",
    ]
)

FIREWORKS_IMAGE_MODELS = _dedupe(
    [
        "FLUX.1-Kontext-Pro",
        "FLUX.1-Kontext-Max",
        "FLUX.1-[dev]-FP8",
        "FLUX.1-[schnell]-FP8",
        "Stable-Diffusion-XL",
        "Qwen3-VL-235B-A22B-Instruct",
        "Qwen3-VL-235B-A22B-Thinking",
        "Molmo2-8B",
        "Molmo2-4B",
        "Qwen3-Omni-30B-A3B-Instruct",
        "Devstral Small 24B Instruct 2512",
        "Qwen3-VL-32B-Instruct",
        "Qwen3-VL-8B-Instruct",
        "Mistral Large-3-675B-Instruct-2512",
        "NVIDIA-Nemotron-Nano-2-VL",
        "Qwen3-VL-30B-A3B-Thinking",
        "Qwen3-VL-30B-A3B-Instruct",
        "GLM-4.5V",
        "Llama-4-Maverick-Instruct (Basic)",
        "Llama-4-Scout-Instruct (Basic)",
        "Qwen2.5-VL-72B-Instruct",
        "Qwen2.5-VL-32B-Instruct",
        "Qwen2.5-VL-7B-Instruct",
        "Qwen2.5-VL-3B-Instruct",
        "Llama-3.2-11B-Vision-Instruct",
        "Llama-3.2-90B-Vision-Instruct",
    ]
)

DEEPGRAM_STT_MODELS = _dedupe(
    [
        "nova-2",
        "nova-2-general",
        "nova-2-meeting",
        "nova-2-phonecall",
        "nova-2-finance",
        "nova-2-conversationalai",
        "nova-2-voicemail",
        "nova-2-video",
        "nova-2-medical",
        "nova-2-drivethru",
        "nova-2-automotive",
        "nova-2-atc",
        "nova",
        "nova-general",
        "nova-phonecall",
        "nova-medical",
    ]
)

ELEVENLABS_TTS_MODELS = _dedupe(
    [
        "eleven_multilingual_v2",
        "eleven_v3",
    ]
)

ELEVENLABS_STT_MODELS = _dedupe(
    [
        "scribe_v2",
        "scribe_v2_realtime",
    ]
)

ELEVENLABS_VOICES = _dedupe(
    [
        "Ellen",
        "Juniper",
        "Jane",
        "James",
        "Arabella",
        "Austin",
        "Jarnathan",
        "Kuon",
        "Blondie",
        "Priyanka",
        "Monika Sogam",
        "Sam",
        "Spuds Oxley",
        "Anika",
        "Celian",
        "Brock",
        "Nathan",
        "Taksh",
        "Viraj",
        "Horatius",
        "Chris",
        "Callum",
        "Laura",
        "Harry",
        "Jessica",
        "Charlotte",
        "Guadeloupe Merryweather",
        "Dr. Von",
        "Grimblewood Thornwhisker",
        "Mark",
    ]
)

CARTESIA_STT_MODELS = _dedupe(
    [
        "ink-whisper",
    ]
)

CARTESIA_TTS_MODELS = _dedupe(
    [
        "sonic-2-2025-06-11",
        "sonic-turbo-2025-03-07",
        "sonic-2024-12-12",
        "sonic-3-2026-01-12",
    ]
)

CARTESIA_VOICES = _dedupe(
    [
        "Tessa",
        "Kiefer",
        "Brandon",
        "Ariana",
        "Dorothy",
        "Joanie",
        "Layla",
        "Marian",
        "Cory",
        "Kyle",
        "Wade 2.0",
        "Sean",
        "Ross",
        "Clint",
        "Celine",
        "Judith",
        "Suzanne",
        "Edward",
        "Tabitha",
        "Elaine",
        "Sterling",
        "Regis",
        "Tanner",
        "Marcus",
        "Colin",
        "Skyler",
        "Cameron",
        "Sabrina",
        "Emily",
        "Shelly",
        "Laurel",
        "Jeremy",
        "Kurt",
        "Zander",
        "Jillian",
        "Theo Silk",
        "Riley",
    ]
)


MODEL_CATALOG: Dict[str, Dict[str, Any]] = {
    "openai": {
        "name": "OpenAI",
        "integration_name": "OpenAI Provider",
        "env_key": "OPENAI_API_KEY",
        "icon_url": "",
        "models": {
            "chat": OPENAI_CHAT_MODELS,
            "translation": OPENAI_CHAT_MODELS,
            "image": OPENAI_IMAGE_MODELS,
            "video": OPENAI_VIDEO_MODELS,
            "stt": OPENAI_STT_MODELS,
            "tts": OPENAI_TTS_MODELS,
            "voice": OPENAI_VOICES,
        },
    },
    "fireworks": {
        "name": "Fireworks AI",
        "integration_name": "Fireworks AI Provider",
        "env_key": "FIREWORKS_API_KEY",
        "icon_url": "",
        "models": {
            "chat": FIREWORKS_CHAT_MODELS,
            "translation": FIREWORKS_CHAT_MODELS,
            "image": FIREWORKS_IMAGE_MODELS,
            "video": [],
            "stt": FIREWORKS_STT_MODELS,
        },
    },
    "xai": {
        "name": "xAI",
        "integration_name": "xAI Provider",
        "env_key": "XAI_API_KEY",
        "icon_url": "",
        "models": {
            "chat": XAI_CHAT_MODELS,
            "translation": XAI_CHAT_MODELS,
            "image": XAI_IMAGE_MODELS,
            "video": XAI_VIDEO_MODELS,
        },
    },
    "openrouter": {
        "name": "OpenRouter",
        "integration_name": "OpenRouter Provider",
        "env_key": "OPENROUTER_API_KEY",
        "icon_url": "",
        "models": {
            "chat": OPENROUTER_CHAT_MODELS,
            "translation": OPENROUTER_CHAT_MODELS,
            "image": [],
            "video": [],
        },
    },
    "elevenlabs": {
        "name": "ElevenLabs",
        "integration_name": "ElevenLabs Voice",
        "env_key": "ELEVENLABS_API_KEY",
        "icon_url": "",
        "models": {
            "stt": ELEVENLABS_STT_MODELS,
            "tts": ELEVENLABS_TTS_MODELS,
            "voice": ELEVENLABS_VOICES,
        },
    },
    "cartesia": {
        "name": "Cartesia",
        "integration_name": "Cartesia Voice",
        "env_key": "CARTESIA_API_KEY",
        "icon_url": "",
        "models": {
            "stt": CARTESIA_STT_MODELS,
            "tts": CARTESIA_TTS_MODELS,
            "voice": CARTESIA_VOICES,
        },
    },
    "google": {
        "name": "Google Cloud",
        "integration_name": "Google Speech Provider",
        "env_key": "GOOGLE_CLOUD_API_KEY",
        "icon_url": "",
        "models": {
            "image": GOOGLE_IMAGE_MODELS,
            "video": GOOGLE_VIDEO_MODELS,
            "stt": [],
            "tts": [],
            "voice": [],
        },
    },
    "azure": {
        "name": "Azure Speech",
        "integration_name": "Azure Speech Provider",
        "env_key": "AZURE_SPEECH_KEY",
        "icon_url": "",
        "models": {
            "stt": [],
            "tts": [],
            "voice": [],
        },
    },
    "aws": {
        "name": "AWS Voice",
        "integration_name": "AWS Voice Provider",
        "env_key": "AWS_ACCESS_KEY_ID",
        "icon_url": "",
        "models": {
            "stt": [],
            "tts": [],
            "voice": [],
        },
    },
    "deepgram": {
        "name": "Deepgram",
        "integration_name": "Deepgram Speech Provider",
        "env_key": "DEEPGRAM_API_KEY",
        "icon_url": "",
        "models": {
            "stt": DEEPGRAM_STT_MODELS,
            "tts": [],
            "voice": [],
        },
    },
    "assemblyai": {
        "name": "AssemblyAI",
        "integration_name": "AssemblyAI Speech Provider",
        "env_key": "ASSEMBLYAI_API_KEY",
        "icon_url": "",
        "models": {
            "stt": [],
            "tts": [],
            "voice": [],
        },
    },
}


INTEGRATION_NAME_TO_PROVIDER = {
    provider["integration_name"]: provider_id for provider_id, provider in MODEL_CATALOG.items()
}


def _has_default_key(provider: Dict[str, Any]) -> bool:
    env_key = provider.get("env_key")
    if not env_key:
        return False
    return bool(getattr(settings, env_key, None))


def _config_has_credentials(config: IntegrationConfigModel, provider: Dict[str, Any]) -> bool:
    if not config.is_active:
        return False
    credentials = config.credentials or {}
    if credentials.get("api_key"):
        return True
    config_data = config.config or {}
    use_default = bool(
        config_data.get("use_default_key")
        or config_data.get("use_default_api_key")
        or config_data.get("use_default_credentials")
    )
    if use_default and _has_default_key(provider):
        return True
    return False


async def _get_provider_statuses(
    db: AsyncSession,
    user_id: int,
) -> Tuple[Set[str], Set[str]]:
    installed: Set[str] = set()
    available: Set[str] = set()

    result = await db.execute(
        select(IntegrationConfigModel, IntegrationModel)
        .join(IntegrationModel, IntegrationConfigModel.integration_id == IntegrationModel.id)
        .where(
            IntegrationConfigModel.user_id == user_id,
            IntegrationConfigModel.is_active.is_(True),
        )
    )

    for config, integration in result.all():
        provider_id = INTEGRATION_NAME_TO_PROVIDER.get(integration.name)
        if not provider_id:
            continue
        installed.add(provider_id)
        provider = MODEL_CATALOG.get(provider_id, {})
        if _config_has_credentials(config, provider):
            available.add(provider_id)

    return installed, available


async def build_model_catalog_response(
    db: AsyncSession,
    user_id: int,
) -> Dict[str, Any]:
    installed, available = await _get_provider_statuses(db, user_id)

    providers_payload: List[Dict[str, Any]] = []
    models_payload: Dict[str, List[Dict[str, Any]]] = {cap: [] for cap in CAPABILITIES}

    for provider_id, provider in MODEL_CATALOG.items():
        provider_models = provider.get("models", {})
        capabilities = [cap for cap, items in provider_models.items() if items]
        providers_payload.append(
            {
                "id": provider_id,
                "name": provider.get("name", provider_id),
                "icon_url": provider.get("icon_url") or None,
                "installed": provider_id in installed,
                "available": provider_id in available,
                "default_env_key": provider.get("env_key"),
                "has_default_key": _has_default_key(provider),
                "capabilities": capabilities,
            }
        )

        if provider_id not in available:
            continue

        for capability, models in provider_models.items():
            if not models:
                continue
            for model in models:
                models_payload.setdefault(capability, []).append(
                    {
                        "provider": provider_id,
                        "model": model,
                        "label": model,
                        "context_window": get_context_window_for_model(model),
                    }
                )

    return {
        "providers": providers_payload,
        "models": models_payload,
    }
