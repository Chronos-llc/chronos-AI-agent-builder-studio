import httpx
import json
from typing import Optional, Dict, Any, List, AsyncIterator
from pydantic import BaseModel, Field
import logging
from enum import Enum

from app.core.config import settings


logger = logging.getLogger(__name__)


class AIProviderType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class AIModelConfig(BaseModel):
    provider_type: AIProviderType
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None


class AIProviderError(Exception):
    """Custom exception for AI provider errors"""
    pass


class AIProviderManager:
    """
    Manager for AI model providers
    
    Handles multiple AI provider connections and provides a unified interface
    for model operations.
    """

    def __init__(self):
        self.providers: Dict[str, AIModelConfig] = {}
        self.default_provider: Optional[str] = None

    async def add_provider(self, provider_id: str, config: AIModelConfig):
        """Add a new AI provider configuration"""
        # Validate the configuration
        if config.provider_type == AIProviderType.OPENAI:
            if not config.api_key and not settings.OPENAI_API_KEY:
                raise AIProviderError("OpenAI API key is required")
            config.api_key = config.api_key or settings.OPENAI_API_KEY
            config.base_url = config.base_url or "https://api.openai.com/v1"
        
        elif config.provider_type == AIProviderType.ANTHROPIC:
            if not config.api_key and not settings.ANTHROPIC_API_KEY:
                raise AIProviderError("Anthropic API key is required")
            config.api_key = config.api_key or settings.ANTHROPIC_API_KEY
            config.base_url = config.base_url or "https://api.anthropic.com/v1"
        
        elif config.provider_type == AIProviderType.OLLAMA:
            config.base_url = config.base_url or "http://localhost:11434"
        
        elif config.provider_type == AIProviderType.CUSTOM:
            if not config.base_url:
                raise AIProviderError("Custom provider requires a base URL")

        self.providers[provider_id] = config
        
        # Set as default if it's the first provider
        if not self.default_provider:
            self.default_provider = provider_id

    async def remove_provider(self, provider_id: str):
        """Remove an AI provider configuration"""
        if provider_id in self.providers:
            del self.providers[provider_id]
            
            # Update default provider if needed
            if self.default_provider == provider_id:
                self.default_provider = next(iter(self.providers.keys()), None)

    async def get_provider(self, provider_id: Optional[str] = None) -> AIModelConfig:
        """Get an AI provider configuration"""
        if not provider_id:
            if not self.default_provider:
                raise AIProviderError("No default AI provider configured")
            return self.providers[self.default_provider]
        
        if provider_id not in self.providers:
            raise AIProviderError(f"AI provider {provider_id} not found")
        
        return self.providers[provider_id]

    async def list_providers(self) -> List[Dict[str, Any]]:
        """List all configured AI providers"""
        return [
            {
                "provider_id": provider_id,
                "config": config.dict(),
                "is_default": provider_id == self.default_provider
            }
            for provider_id, config in self.providers.items()
        ]

    async def generate_text(
        self,
        prompt: str,
        provider_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using the specified AI provider"""
        config = await self.get_provider(provider_id)
        
        if config.provider_type == AIProviderType.OPENAI:
            return await self._openai_generate_text(config, prompt, **kwargs)
        elif config.provider_type == AIProviderType.ANTHROPIC:
            return await self._anthropic_generate_text(config, prompt, **kwargs)
        elif config.provider_type == AIProviderType.OLLAMA:
            return await self._ollama_generate_text(config, prompt, **kwargs)
        elif config.provider_type == AIProviderType.CUSTOM:
            return await self._custom_generate_text(config, prompt, **kwargs)
        else:
            raise AIProviderError(f"Unsupported provider type: {config.provider_type}")

    async def stream_text(
        self,
        prompt: str,
        provider_id: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream text generation using the specified AI provider"""
        config = await self.get_provider(provider_id)
        
        if config.provider_type == AIProviderType.OPENAI:
            async for chunk in self._openai_stream_text(config, prompt, **kwargs):
                yield chunk
        elif config.provider_type == AIProviderType.ANTHROPIC:
            async for chunk in self._anthropic_stream_text(config, prompt, **kwargs):
                yield chunk
        elif config.provider_type == AIProviderType.OLLAMA:
            async for chunk in self._ollama_stream_text(config, prompt, **kwargs):
                yield chunk
        elif config.provider_type == AIProviderType.CUSTOM:
            async for chunk in self._custom_stream_text(config, prompt, **kwargs):
                yield chunk
        else:
            raise AIProviderError(f"Unsupported provider type: {config.provider_type}")

    async def _openai_generate_text(
        self,
        config: AIModelConfig,
        prompt: str,
        **kwargs
    ) -> str:
        """Generate text using OpenAI API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
        ) as client:
            payload = {
                "model": config.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
                "temperature": kwargs.get("temperature", config.temperature),
                "top_p": kwargs.get("top_p", config.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", config.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", config.presence_penalty),
            }
            
            if config.stop_sequences:
                payload["stop"] = config.stop_sequences
            
            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _openai_stream_text(
        self,
        config: AIModelConfig,
        prompt: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream text generation using OpenAI API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
        ) as client:
            payload = {
                "model": config.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
                "temperature": kwargs.get("temperature", config.temperature),
                "top_p": kwargs.get("top_p", config.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", config.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", config.presence_penalty),
                "stream": True
            }
            
            if config.stop_sequences:
                payload["stop"] = config.stop_sequences
            
            async with client.stream("POST", "/chat/completions", json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk.get("choices") and chunk["choices"][0].get("delta").get("content"):
                                yield chunk["choices"][0]["delta"]["content"]
                        except json.JSONDecodeError:
                            continue

    async def _anthropic_generate_text(
        self,
        config: AIModelConfig,
        prompt: str,
        **kwargs
    ) -> str:
        """Generate text using Anthropic API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=60.0,
            headers={
                "x-api-key": config.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
        ) as client:
            payload = {
                "model": config.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
                "temperature": kwargs.get("temperature", config.temperature),
                "top_p": kwargs.get("top_p", config.top_p),
            }
            
            if config.stop_sequences:
                payload["stop_sequences"] = config.stop_sequences
            
            response = await client.post("/messages", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["content"][0]["text"]

    async def _anthropic_stream_text(
        self,
        config: AIModelConfig,
        prompt: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream text generation using Anthropic API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=60.0,
            headers={
                "x-api-key": config.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
        ) as client:
            payload = {
                "model": config.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
                "temperature": kwargs.get("temperature", config.temperature),
                "top_p": kwargs.get("top_p", config.top_p),
                "stream": True
            }
            
            if config.stop_sequences:
                payload["stop_sequences"] = config.stop_sequences
            
            async with client.stream("POST", "/messages", json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk.get("delta") and chunk["delta"].get("text"):
                                yield chunk["delta"]["text"]
                        except json.JSONDecodeError:
                            continue

    async def _ollama_generate_text(
        self,
        config: AIModelConfig,
        prompt: str,
        **kwargs
    ) -> str:
        """Generate text using Ollama API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=60.0,
            headers={"Content-Type": "application/json"}
        ) as client:
            payload = {
                "model": config.model_name,
                "prompt": prompt,
                "options": {
                    "temperature": kwargs.get("temperature", config.temperature),
                    "top_p": kwargs.get("top_p", config.top_p),
                    "num_predict": kwargs.get("max_tokens", config.max_tokens),
                }
            }
            
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["response"]

    async def _ollama_stream_text(
        self,
        config: AIModelConfig,
        prompt: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream text generation using Ollama API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=60.0,
            headers={"Content-Type": "application/json"}
        ) as client:
            payload = {
                "model": config.model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", config.temperature),
                    "top_p": kwargs.get("top_p", config.top_p),
                    "num_predict": kwargs.get("max_tokens", config.max_tokens),
                }
            }
            
            async with client.stream("POST", "/api/generate", json=payload) as response:
                async for line in response.aiter_lines():
                    try:
                        chunk = json.loads(line)
                        if chunk.get("response"):
                            yield chunk["response"]
                    except json.JSONDecodeError:
                        continue

    async def _custom_generate_text(
        self,
        config: AIModelConfig,
        prompt: str,
        **kwargs
    ) -> str:
        """Generate text using custom API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=60.0,
            headers={"Content-Type": "application/json"}
        ) as client:
            # Custom providers may have different API structures
            # This is a basic implementation that can be customized
            payload = {
                "model": config.model_name,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
                "temperature": kwargs.get("temperature", config.temperature),
            }
            
            response = await client.post("/generate", json=payload)
            response.raise_for_status()
            
            result = response.json()
            # Try to extract text from common response structures
            if "text" in result:
                return result["text"]
            elif "content" in result:
                return result["content"]
            elif "response" in result:
                return result["response"]
            else:
                return str(result)

    async def _custom_stream_text(
        self,
        config: AIModelConfig,
        prompt: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream text generation using custom API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=60.0,
            headers={"Content-Type": "application/json"}
        ) as client:
            payload = {
                "model": config.model_name,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", config.max_tokens),
                "temperature": kwargs.get("temperature", config.temperature),
                "stream": True
            }
            
            async with client.stream("POST", "/generate", json=payload) as response:
                async for line in response.aiter_lines():
                    try:
                        chunk = json.loads(line)
                        # Try to extract text from common response structures
                        if "text" in chunk:
                            yield chunk["text"]
                        elif "content" in chunk:
                            yield chunk["content"]
                        elif "response" in chunk:
                            yield chunk["response"]
                    except json.JSONDecodeError:
                        continue

    async def list_models(self, provider_id: Optional[str] = None) -> List[str]:
        """List available models from a provider"""
        config = await self.get_provider(provider_id)
        
        if config.provider_type == AIProviderType.OPENAI:
            return await self._openai_list_models(config)
        elif config.provider_type == AIProviderType.ANTHROPIC:
            return await self._anthropic_list_models(config)
        elif config.provider_type == AIProviderType.OLLAMA:
            return await self._ollama_list_models(config)
        else:
            # For custom providers, return a default list or implement custom logic
            return [config.model_name]

    async def _openai_list_models(self, config: AIModelConfig) -> List[str]:
        """List available models from OpenAI API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
        ) as client:
            response = await client.get("/models")
            response.raise_for_status()
            
            result = response.json()
            return [model["id"] for model in result["data"]]

    async def _anthropic_list_models(self, config: AIModelConfig) -> List[str]:
        """List available models from Anthropic API"""
        # Anthropic doesn't have a public models endpoint, so return known models
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ]

    async def _ollama_list_models(self, config: AIModelConfig) -> List[str]:
        """List available models from Ollama API"""
        async with httpx.AsyncClient(
            base_url=config.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        ) as client:
            response = await client.get("/api/tags")
            response.raise_for_status()
            
            result = response.json()
            return [model["name"] for model in result["models"]]


# Global AI provider manager instance
ai_provider_manager = AIProviderManager()


async def initialize_ai_providers():
    """Initialize AI providers from configuration"""
    try:
        # Initialize default providers if API keys are available
        if settings.OPENAI_API_KEY:
            openai_config = AIModelConfig(
                provider_type=AIProviderType.OPENAI,
                model_name="gpt-4",
                api_key=settings.OPENAI_API_KEY,
                max_tokens=4096,
                temperature=0.7
            )
            await ai_provider_manager.add_provider("openai", openai_config)

        if settings.ANTHROPIC_API_KEY:
            anthropic_config = AIModelConfig(
                provider_type=AIProviderType.ANTHROPIC,
                model_name="claude-3-sonnet-20240229",
                api_key=settings.ANTHROPIC_API_KEY,
                max_tokens=4096,
                temperature=0.7
            )
            await ai_provider_manager.add_provider("anthropic", anthropic_config)

        # Add Ollama as a local provider
        ollama_config = AIModelConfig(
            provider_type=AIProviderType.OLLAMA,
            model_name="llama3",
            base_url="http://localhost:11434",
            max_tokens=4096,
            temperature=0.7
        )
        await ai_provider_manager.add_provider("ollama", ollama_config)

        logger.info("AI providers initialized")
    except Exception as e:
        logger.error(f"Failed to initialize AI providers: {e}")


async def get_ai_provider() -> AIProviderManager:
    """Get the AI provider manager"""
    return ai_provider_manager