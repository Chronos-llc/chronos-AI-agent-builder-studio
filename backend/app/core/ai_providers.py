"""
AI Provider integrations for Chronos AI Agent Builder Studio
"""
import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import httpx
import logging

from app.core.config import settings
from app.core.model_catalog import MODEL_CATALOG

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from the AI provider"""
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.openai.com/v1")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0)
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"OpenAI API error: {e}")
            return {"error": str(e)}
    
    async def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = await self.client.get(
                f"{self.base_url}/models",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return [model["id"] for model in data.get("data", [])]
        except httpx.HTTPError as e:
            logger.error(f"Error fetching OpenAI models: {e}")
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]  # Fallback models


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.anthropic.com/v1")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "claude-3-haiku-20240307",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using Anthropic Claude API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages format for Claude
        system_message = ""
        claude_messages = []
        
        for message in messages:
            if message["role"] == "system":
                system_message = message["content"]
            else:
                claude_messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
        
        payload = {
            "model": model,
            "messages": claude_messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "system": system_message if system_message else None
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Anthropic API error: {e}")
            return {"error": str(e)}
    
    async def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        # Anthropic doesn't have a models endpoint, return known models
        return [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229",
            "claude-3-opus-20240229"
        ]


class AIProviderManager:
    """Manager for AI providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self._initialize_providers()
        
    def get_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        """Get an AI provider instance by name"""
        return self.providers.get(provider_name)
    
    def _initialize_providers(self):
        """Initialize available AI providers"""
        # Initialize OpenAI if API key is available
        if settings.OPENAI_API_KEY:
            self.providers["openai"] = OpenAIProvider(settings.OPENAI_API_KEY)
            logger.info("OpenAI provider initialized")
        
        # Initialize Anthropic if API key is available
        if settings.ANTHROPIC_API_KEY:
            self.providers["anthropic"] = AnthropicProvider(settings.ANTHROPIC_API_KEY)
            logger.info("Anthropic provider initialized")
        
        if not self.providers:
            logger.warning("No AI providers initialized. Install providers and add API keys to enable models.")
    
    async def generate_response(
        self, 
        provider_name: str,
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using specified provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not available")
        
        provider = self.providers[provider_name]
        return await provider.generate_response(messages, model, **kwargs)
    
    async def get_available_models(self, provider_name: str) -> List[str]:
        """Get available models for a provider"""
        if provider_name not in self.providers:
            return []
        
        provider = self.providers[provider_name]
        return await provider.get_available_models()
    
    async def get_all_available_models(self) -> Dict[str, List[str]]:
        """Get all available models across all providers"""
        tasks = []
        for provider_name, provider in self.providers.items():
            tasks.append(self.get_available_models(provider_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        models = {}
        for i, (provider_name, _) in enumerate(self.providers.items()):
            if isinstance(results[i], Exception):
                logger.error(f"Error getting models for {provider_name}: {results[i]}")
                models[provider_name] = []
            else:
                models[provider_name] = results[i]
        
        return models
    
    async def close_all(self):
        """Close all provider connections"""
        for provider in self.providers.values():
            await provider.close()


# Global AI provider manager instance
ai_provider_manager = AIProviderManager()


class PromptAIProvider:
    """Adapter that provides a prompt-based interface over chat providers."""

    def __init__(self, provider_name: str, provider: BaseAIProvider):
        self.provider_name = provider_name
        self.provider = provider

    async def generate_response(self, prompt: str, model: str, **kwargs) -> str:
        """Generate a response from a prompt string."""
        messages = [{"role": "user", "content": prompt}]
        response = await self.provider.generate_response(messages=messages, model=model, **kwargs)
        return _extract_response_text(self.provider_name, response)


def _extract_response_text(provider_name: str, response: Dict[str, Any]) -> str:
    """Extract a text response from provider payloads."""
    if isinstance(response, dict) and response.get("error"):
        raise ValueError(response["error"])

    if isinstance(response, dict):
        # OpenAI-style response
        if "choices" in response and response["choices"]:
            choice = response["choices"][0]
            message = choice.get("message") or {}
            content = message.get("content") or choice.get("text")
            if content is not None:
                return str(content)

        # Anthropic-style response
        if "content" in response:
            content = response["content"]
            if isinstance(content, list):
                parts = [
                    part.get("text", "")
                    for part in content
                    if isinstance(part, dict)
                ]
                text = "".join(parts).strip()
                if text:
                    return text
            if isinstance(content, str):
                return content

    return str(response)


async def initialize_ai_providers():
    """Initialize AI providers (called on startup)"""
    logger.info("Initializing AI providers...")
    # The manager is already initialized in __init__
    # This function can be used for any additional setup
    pass


def get_ai_provider(provider_name: str) -> Optional[PromptAIProvider]:
    """Get a prompt-based AI provider adapter by name."""
    provider = ai_provider_manager.providers.get(provider_name)
    if not provider:
        return None
    return PromptAIProvider(provider_name, provider)


async def get_ai_response(
    provider: str,
    messages: List[Dict[str, str]], 
    model: str,
    **kwargs
) -> Dict[str, Any]:
    """Get AI response using the global provider manager"""
    return await ai_provider_manager.generate_response(provider, messages, model, **kwargs)


async def get_available_models(provider: str) -> List[str]:
    """Get available models for a provider"""
    return await ai_provider_manager.get_available_models(provider)


async def get_all_models() -> Dict[str, List[str]]:
    """Get all available models across all providers"""
    return await ai_provider_manager.get_all_available_models()

def get_raw_ai_provider(provider_name: str) -> Optional[BaseAIProvider]:
    """Get an AI provider instance by name"""
    global ai_provider_manager
    return ai_provider_manager.get_provider(provider_name)


# Utility functions for agent configuration
def get_default_model_config(provider: str) -> Dict[str, Any]:
    """Get default model configuration for a provider"""
    configs = {
        "openai": {
            "model": "gpt-3.5-turbo",
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        },
        "anthropic": {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 1.0
        },
        "fireworks": {
            "model": "gpt-oss-20B",
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 1.0
        },
        "xai": {
            "model": "grok-3",
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 1.0
        },
        "openrouter": {
            "model": "GPT-5.2-Chat",
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 1.0
        }
    }
    
    return configs.get(provider, configs["openai"])


def validate_model_config(provider: str, config: Dict[str, Any]) -> bool:
    """Validate model configuration"""
    required_fields = ["model"]
    
    # Check required fields
    for field in required_fields:
        if field not in config:
            return False
    
    catalog = MODEL_CATALOG.get(provider)
    if not catalog:
        return True

    model_name = config.get("model")
    if model_name == "auto":
        return True

    available_models = set()
    for models in catalog.get("models", {}).values():
        available_models.update(models)

    if model_name in available_models:
        return True

    # Allow case-insensitive matches to avoid breaking legacy configs.
    available_lower = {model.lower() for model in available_models}
    if isinstance(model_name, str) and model_name.lower() in available_lower:
        return True

    # Allow custom models not yet listed in the catalog.
    return True
