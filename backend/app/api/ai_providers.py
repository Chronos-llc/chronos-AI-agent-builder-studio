from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.core.ai_providers import (
    AIModelConfig,
    AIProviderType,
    ai_provider_manager,
    AIProviderError
)
from app.core.security import get_current_user
from app.models.user import User as UserModel


router = APIRouter()


class AIProviderCreate(BaseModel):
    provider_id: str
    config: AIModelConfig


class AIProviderResponse(BaseModel):
    provider_id: str
    provider_type: AIProviderType
    model_name: str
    is_default: bool


class AIProviderListResponse(BaseModel):
    providers: List[AIProviderResponse]
    default_provider: Optional[str]


class AITextRequest(BaseModel):
    prompt: str
    provider_id: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None


class AITextResponse(BaseModel):
    text: str
    provider: str
    model: str
    tokens_used: int


class AIStreamRequest(BaseModel):
    prompt: str
    provider_id: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None


@router.post("/ai/providers/", response_model=AIProviderResponse)
async def add_ai_provider(
    provider_data: AIProviderCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """Add a new AI provider configuration"""
    try:
        await ai_provider_manager.add_provider(provider_data.provider_id, provider_data.config)
        
        config = await ai_provider_manager.get_provider(provider_data.provider_id)
        return AIProviderResponse(
            provider_id=provider_data.provider_id,
            provider_type=config.provider_type,
            model_name=config.model_name,
            is_default=provider_data.provider_id == ai_provider_manager.default_provider
        )
    except AIProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add AI provider: {str(e)}")


@router.delete("/ai/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_ai_provider(
    provider_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Remove an AI provider configuration"""
    try:
        await ai_provider_manager.remove_provider(provider_id)
    except AIProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove AI provider: {str(e)}")


@router.get("/ai/providers/", response_model=AIProviderListResponse)
async def list_ai_providers(
    current_user: UserModel = Depends(get_current_user)
):
    """List all configured AI providers"""
    providers = await ai_provider_manager.list_providers()
    
    return AIProviderListResponse(
        providers=[
            AIProviderResponse(
                provider_id=p["provider_id"],
                provider_type=p["config"]["provider_type"],
                model_name=p["config"]["model_name"],
                is_default=p["is_default"]
            )
            for p in providers
        ],
        default_provider=ai_provider_manager.default_provider
    )


@router.post("/ai/generate/", response_model=AITextResponse)
async def generate_text(
    text_request: AITextRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Generate text using AI provider"""
    try:
        result = await ai_provider_manager.generate_text(
            text_request.prompt,
            text_request.provider_id,
            max_tokens=text_request.max_tokens,
            temperature=text_request.temperature,
            top_p=text_request.top_p
        )
        
        # Get provider info for response
        config = await ai_provider_manager.get_provider(text_request.provider_id)
        
        return AITextResponse(
            text=result,
            provider=config.provider_type,
            model=config.model_name,
            tokens_used=len(result.split())  # Simple token estimation
        )
    except AIProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")


@router.post("/ai/stream/")
async def stream_text(
    stream_request: AIStreamRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Stream text generation using AI provider"""
    try:
        async def generate():
            async for chunk in ai_provider_manager.stream_text(
                stream_request.prompt,
                stream_request.provider_id,
                max_tokens=stream_request.max_tokens,
                temperature=stream_request.temperature,
                top_p=stream_request.top_p
            ):
                yield f"data: {chunk}\n\n"
        
        return generate()
    except AIProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text streaming failed: {str(e)}")


@router.get("/ai/models/", response_model=Dict[str, List[str]])
async def list_models(
    provider_id: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user)
):
    """List available models from AI providers"""
    try:
        models = await ai_provider_manager.list_models(provider_id)
        
        if provider_id:
            return {"models": models}
        else:
            # Return models for all providers
            result = {}
            providers = await ai_provider_manager.list_providers()
            
            for provider in providers:
                provider_id = provider["provider_id"]
                provider_models = await ai_provider_manager.list_models(provider_id)
                result[provider_id] = provider_models
            
            return result
    except AIProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/ai/health/", response_model=Dict[str, Any])
async def ai_health_check(
    current_user: UserModel = Depends(get_current_user)
):
    """Check AI provider health status"""
    health_status = {}
    
    providers = await ai_provider_manager.list_providers()
    
    for provider in providers:
        provider_id = provider["provider_id"]
        try:
            # Test a simple completion to check health
            test_prompt = "Hello, this is a test."
            result = await ai_provider_manager.generate_text(test_prompt, provider_id, max_tokens=5)
            
            health_status[provider_id] = {
                "status": "healthy",
                "response_time": "fast",  # Would be measured in real implementation
                "model": provider["config"]["model_name"]
            }
        except Exception as e:
            health_status[provider_id] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    return {
        "status": "ok",
        "providers": health_status,
        "default_provider": ai_provider_manager.default_provider
    }