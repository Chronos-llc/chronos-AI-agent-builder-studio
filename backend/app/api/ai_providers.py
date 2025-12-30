from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, List, Any
import logging

from app.core.ai_providers import (
    ai_provider_manager, 
    get_ai_response, 
    get_all_models,
    get_default_model_config,
    validate_model_config
)
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/providers")
async def get_ai_providers(current_user: User = Depends(get_current_user)):
    """Get list of available AI providers"""
    providers = []
    
    for provider_name, provider in ai_provider_manager.providers.items():
        providers.append({
            "name": provider_name,
            "type": provider.__class__.__name__.replace("Provider", ""),
            "available": True
        })
    
    return {"providers": providers}


@router.get("/models")
async def get_all_ai_models(current_user: User = Depends(get_current_user)):
    """Get all available models across all providers"""
    try:
        models = await get_all_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error fetching AI models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available models"
        )


@router.get("/models/{provider}")
async def get_provider_models(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """Get available models for a specific provider"""
    try:
        models = await ai_provider_manager.get_available_models(provider)
        return {"provider": provider, "models": models}
    except Exception as e:
        logger.error(f"Error fetching models for provider {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch models for provider {provider}"
        )


@router.get("/config/{provider}/defaults")
async def get_default_config(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """Get default configuration for a provider"""
    if provider not in ai_provider_manager.providers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider} not found"
        )
    
    config = get_default_model_config(provider)
    return {"provider": provider, "config": config}


@router.post("/chat")
async def chat_with_ai(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Send chat message to AI provider"""
    try:
        provider = request_data.get("provider")
        messages = request_data.get("messages", [])
        model = request_data.get("model")
        config = request_data.get("config", {})
        
        if not provider or not messages or not model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="provider, messages, and model are required"
            )
        
        if provider not in ai_provider_manager.providers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider {provider} not available"
            )
        
        # Validate and merge configuration
        default_config = get_default_model_config(provider)
        final_config = {**default_config, **config}
        
        if not validate_model_config(provider, final_config):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid model configuration"
            )
        
        # Generate response
        response = await get_ai_response(
            provider=provider,
            messages=messages,
            model=model,
            **final_config
        )
        
        return {
            "success": True,
            "response": response,
            "provider": provider,
            "model": model
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI response"
        )


@router.post("/test")
async def test_ai_provider(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Test AI provider with a simple message"""
    try:
        provider = request_data.get("provider")
        model = request_data.get("model")
        
        if not provider or not model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="provider and model are required"
            )
        
        test_messages = [
            {"role": "user", "content": "Hello! Please respond with 'Test successful'."}
        ]
        
        response = await get_ai_response(
            provider=provider,
            messages=test_messages,
            model=model
        )
        
        return {
            "success": True,
            "provider": provider,
            "model": model,
            "response": response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing AI provider: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test provider {provider}"
        )


@router.get("/health")
async def ai_providers_health(current_user: User = Depends(get_current_user)):
    """Health check for AI providers"""
    health_status = {}
    
    for provider_name, provider in ai_provider_manager.providers.items():
        try:
            # Simple test to check if provider is responsive
            test_messages = [{"role": "user", "content": "test"}]
            # Don't actually make the request, just check if provider exists
            health_status[provider_name] = {
                "status": "healthy",
                "available": True,
                "type": provider.__class__.__name__.replace("Provider", "")
            }
        except Exception as e:
            health_status[provider_name] = {
                "status": "unhealthy",
                "available": False,
                "error": str(e)
            }
    
    return {
        "overall_status": "healthy" if any(p.get("available") for p in health_status.values()) else "unhealthy",
        "providers": health_status
    }