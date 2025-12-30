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


class MockAIProvider(BaseAIProvider):
    """Mock AI provider for testing"""
    
    def __init__(self):
        super().__init__("")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "mock-model",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate mock response"""
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Extract user message
        user_message = ""
        for message in messages:
            if message["role"] == "user":
                user_message = message["content"]
                break
        
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": f"This is a mock response to: {user_message}"
                }
            }],
            "model": model,
            "usage": {
                "prompt_tokens": len(user_message.split()) * 1.3,
                "completion_tokens": 50,
                "total_tokens": len(user_message.split()) * 1.3 + 50
            }
        }
    
    async def get_available_models(self) -> List[str]:
        """Get mock available models"""
        return ["mock-model", "mock-gpt", "mock-claude"]


class AIProviderManager:
    """Manager for AI providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self._initialize_providers()
    
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
        
        # Always initialize mock provider for testing
        self.providers["mock"] = MockAIProvider()
        logger.info("Mock provider initialized")
    
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


async def initialize_ai_providers():
    """Initialize AI providers (called on startup)"""
    logger.info("Initializing AI providers...")
    # The manager is already initialized in __init__
    # This function can be used for any additional setup
    pass


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
        "mock": {
            "model": "mock-model",
            "max_tokens": 1000,
            "temperature": 0.7
        }
    }
    
    return configs.get(provider, configs["mock"])


def validate_model_config(provider: str, config: Dict[str, Any]) -> bool:
    """Validate model configuration"""
    required_fields = ["model"]
    
    # Check required fields
    for field in required_fields:
        if field not in config:
            return False
    
    # Provider-specific validation
    if provider == "openai":
        return config["model"] in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    elif provider == "anthropic":
        return config["model"] in [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229", 
            "claude-3-opus-20240229"
        ]
    elif provider == "mock":
        return True
    
    return False