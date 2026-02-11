"""
Seed AI provider integrations into the database.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.future import select
from app.core.database import async_session_maker
from app.models.integration import Integration as IntegrationModel
from app.models.user import User as UserModel


def build_config_schema():
    return {
        "type": "object",
        "properties": {
            "use_default_key": {
                "type": "boolean",
                "title": "Use Studio Default API Key",
                "description": "Use the API key from the studio .env file when enabled.",
                "default": True,
            }
        },
        "required": [],
    }


def build_credentials_schema():
    return {
        "type": "object",
        "properties": {
            "api_key": {
                "type": "string",
                "title": "API Key",
                "description": "Your provider API key",
                "sensitive": True,
            }
        },
        "required": [],
    }


PROVIDERS = [
    {
        "name": "OpenAI Provider",
        "description": "OpenAI models for chat, translation, vision, and speech.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://platform.openai.com/docs",
        "version": "1.0.0",
        "supported_features": ["chat", "translation", "image", "video", "stt", "tts", "voice"],
    },
    {
        "name": "Fireworks AI Provider",
        "description": "Fireworks AI models for chat and reasoning.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://docs.fireworks.ai",
        "version": "1.0.0",
        "supported_features": ["chat", "translation", "image", "stt"],
    },
    {
        "name": "xAI Provider",
        "description": "xAI Grok models for chat and reasoning.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://docs.x.ai",
        "version": "1.0.0",
        "supported_features": ["chat", "translation", "image", "video"],
    },
    {
        "name": "OpenRouter Provider",
        "description": "OpenRouter aggregation for multiple LLMs.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://openrouter.ai/docs",
        "version": "1.0.0",
        "supported_features": ["chat", "translation"],
    },
    {
        "name": "ElevenLabs Voice",
        "description": "ElevenLabs text-to-speech and voice generation.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://elevenlabs.io/docs",
        "version": "1.0.0",
        "supported_features": ["stt", "tts", "voice"],
    },
    {
        "name": "Cartesia Voice",
        "description": "Cartesia speech-to-text, text-to-speech, and voice models.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://docs.cartesia.ai",
        "version": "1.0.0",
        "supported_features": ["stt", "tts", "voice"],
    },
    {
        "name": "Google Speech Provider",
        "description": "Google Cloud Speech-to-Text and Text-to-Speech.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://cloud.google.com/speech-to-text/docs",
        "version": "1.0.0",
        "supported_features": ["image", "video", "stt", "tts", "voice"],
    },
    {
        "name": "Azure Speech Provider",
        "description": "Azure Cognitive Services speech models.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://learn.microsoft.com/azure/ai-services/speech-service/",
        "version": "1.0.0",
        "supported_features": ["stt", "tts", "voice"],
    },
    {
        "name": "AWS Voice Provider",
        "description": "AWS Transcribe and Polly speech services.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://docs.aws.amazon.com/transcribe/",
        "version": "1.0.0",
        "supported_features": ["stt", "tts", "voice"],
    },
    {
        "name": "Deepgram Speech Provider",
        "description": "Deepgram speech-to-text models.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://developers.deepgram.com/docs",
        "version": "1.0.0",
        "supported_features": ["stt"],
    },
    {
        "name": "AssemblyAI Speech Provider",
        "description": "AssemblyAI speech-to-text models.",
        "integration_type": "ai_model",
        "category": "ai_models",
        "icon": "AI",
        "documentation_url": "https://www.assemblyai.com/docs",
        "version": "1.0.0",
        "supported_features": ["stt"],
    },
]


async def seed_ai_providers():
    async with async_session_maker() as session:
        result = await session.execute(select(UserModel).limit(1))
        user = result.scalars().first()
        if not user:
            print("No users found. Please create a user first.")
            return

        for provider in PROVIDERS:
            existing = await session.execute(
                select(IntegrationModel).where(IntegrationModel.name == provider["name"])
            )
            if existing.scalars().first():
                print(f"{provider['name']} integration already exists")
                continue

            integration = IntegrationModel(
                name=provider["name"],
                description=provider["description"],
                integration_type=provider["integration_type"],
                category=provider["category"],
                icon=provider["icon"],
                documentation_url=provider["documentation_url"],
                version=provider["version"],
                is_public=True,
                download_count=0,
                rating=0.0,
                review_count=0,
                author_id=user.id,
                config_schema=build_config_schema(),
                credentials_schema=build_credentials_schema(),
                supported_features=provider["supported_features"],
            )

            session.add(integration)
            await session.commit()
            await session.refresh(integration)
            print(f"Created integration: {provider['name']}")


if __name__ == "__main__":
    asyncio.run(seed_ai_providers())
