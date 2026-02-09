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
        "Llama-3.3-70B-instuct",
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
        "Olmo-3,1-32B-instruct",
        "Mistral-small-creative",
        "Olmo-3.1-32B-Think",
        "MiMo-V2-Flash",
        "GPT-5.2-Chat",
        "Deepseek-V3-2-Speciale",
    ]
)


MODEL_CATALOG: Dict[str, Dict[str, Any]] = {
    "openai": {
        "name": "OpenAI",
        "integration_name": "OpenAI Provider",
        "env_key": "OPENAI_API_KEY",
        "models": {
            "chat": OPENAI_CHAT_MODELS,
            "translation": OPENAI_CHAT_MODELS,
            "image": ["gpt-image-1", "dall-e-3", "dall-e-2"],
            "video": ["sora"],
            "stt": ["whisper-1"],
            "tts": ["tts-1", "tts-1-hd"],
            "voice": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        },
    },
    "fireworks": {
        "name": "Fireworks AI",
        "integration_name": "Fireworks AI Provider",
        "env_key": "FIREWORKS_API_KEY",
        "models": {
            "chat": FIREWORKS_CHAT_MODELS,
            "translation": FIREWORKS_CHAT_MODELS,
            "image": [],
            "video": [],
        },
    },
    "xai": {
        "name": "xAI",
        "integration_name": "xAI Provider",
        "env_key": "XAI_API_KEY",
        "models": {
            "chat": XAI_CHAT_MODELS,
            "translation": XAI_CHAT_MODELS,
            "image": [],
            "video": [],
        },
    },
    "openrouter": {
        "name": "OpenRouter",
        "integration_name": "OpenRouter Provider",
        "env_key": "OPENROUTER_API_KEY",
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
        "models": {
            "tts": ["eleven_multilingual_v2"],
            "voice": [],
        },
    },
    "google": {
        "name": "Google Cloud",
        "integration_name": "Google Speech Provider",
        "env_key": "GOOGLE_CLOUD_API_KEY",
        "models": {
            "stt": [],
            "tts": [],
            "voice": [],
        },
    },
    "azure": {
        "name": "Azure Speech",
        "integration_name": "Azure Speech Provider",
        "env_key": "AZURE_SPEECH_KEY",
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
        "models": {
            "stt": ["nova-2"],
            "tts": [],
            "voice": [],
        },
    },
    "assemblyai": {
        "name": "AssemblyAI",
        "integration_name": "AssemblyAI Speech Provider",
        "env_key": "ASSEMBLYAI_API_KEY",
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
    models_payload: Dict[str, List[Dict[str, str]]] = {cap: [] for cap in CAPABILITIES}

    for provider_id, provider in MODEL_CATALOG.items():
        provider_models = provider.get("models", {})
        capabilities = [cap for cap, items in provider_models.items() if items]
        providers_payload.append(
            {
                "id": provider_id,
                "name": provider.get("name", provider_id),
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
                    }
                )

    return {
        "providers": providers_payload,
        "models": models_payload,
    }
