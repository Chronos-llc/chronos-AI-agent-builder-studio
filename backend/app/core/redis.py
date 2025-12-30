import redis.asyncio as redis
from typing import Optional, Any
import json
import pickle
from app.core.config import settings

# Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get or create Redis client"""
    global redis_client
    
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL)
    
    return redis_client


async def close_redis_connection():
    """Close Redis connection"""
    global redis_client
    
    if redis_client:
        await redis_client.close()
        redis_client = None


async def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """Set value in Redis cache"""
    try:
        client = await get_redis_client()
        
        # Serialize value
        if isinstance(value, (dict, list)):
            serialized_value = json.dumps(value, default=str)
        else:
            serialized_value = pickle.dumps(value)
        
        await client.setex(key, expire, serialized_value)
        return True
    except Exception:
        return False


async def get_cache(key: str) -> Optional[Any]:
    """Get value from Redis cache"""
    try:
        client = await get_redis_client()
        
        value = await client.get(key)
        if value is None:
            return None
        
        # Try to deserialize as JSON first
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # If JSON fails, try pickle
            try:
                return pickle.loads(value)
            except Exception:
                return value.decode('utf-8')
    except Exception:
        return None


async def delete_cache(key: str) -> bool:
    """Delete value from Redis cache"""
    try:
        client = await get_redis_client()
        await client.delete(key)
        return True
    except Exception:
        return False


async def exists_cache(key: str) -> bool:
    """Check if key exists in Redis cache"""
    try:
        client = await get_redis_client()
        result = await client.exists(key)
        return bool(result)
    except Exception:
        return False


# Session management
async def set_session(session_id: str, user_data: dict, expire: int = 86400) -> bool:
    """Set user session data"""
    session_key = f"session:{session_id}"
    return await set_cache(session_key, user_data, expire)


async def get_session(session_id: str) -> Optional[dict]:
    """Get user session data"""
    session_key = f"session:{session_id}"
    return await get_cache(session_key)


async def delete_session(session_id: str) -> bool:
    """Delete user session"""
    session_key = f"session:{session_id}"
    return await delete_cache(session_key)


# Rate limiting
async def check_rate_limit(key: str, limit: int, window: int = 60) -> bool:
    """Check if rate limit is exceeded"""
    try:
        client = await get_redis_client()
        
        # Use Redis pipeline for atomic operations
        pipe = client.pipeline()
        pipe.incr(f"rate_limit:{key}")
        pipe.expire(f"rate_limit:{key}", window)
        results = await pipe.execute()
        
        current_count = results[0]
        return current_count <= limit
    except Exception:
        return False


# User activity tracking
async def track_user_activity(user_id: str, action: str) -> None:
    """Track user activity"""
    try:
        client = await get_redis_client()
        
        # Track recent activity (last 100 actions)
        activity_key = f"activity:{user_id}"
        pipe = client.pipeline()
        
        # Add new activity
        pipe.lpush(activity_key, f"{action}:{int(time.time())}")
        pipe.ltrim(activity_key, 0, 99)  # Keep only last 100 activities
        pipe.expire(activity_key, 86400)  # 24 hours
        
        await pipe.execute()
    except Exception:
        pass


# Blacklisted tokens (for logout)
async def blacklist_token(jti: str, expire: int = 86400) -> bool:
    """Blacklist a JWT token"""
    token_key = f"blacklist:{jti}"
    return await set_cache(token_key, True, expire)


async def is_token_blacklisted(jti: str) -> bool:
    """Check if token is blacklisted"""
    token_key = f"blacklist:{jti}"
    return await exists_cache(token_key)


import time