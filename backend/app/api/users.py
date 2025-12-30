from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.auth import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    
    # Check if email is being updated and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        result = await db.execute(select(User).where(User.email == user_update.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if username is being updated and if it's already taken
    if user_update.username and user_update.username != current_user.username:
        result = await db.execute(select(User).where(User.username == user_update.username))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.delete("/me")
async def delete_current_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete current user account"""
    
    # In a real application, you might want to soft delete or archive instead
    await db.delete(current_user)
    await db.commit()
    
    return {"message": "Account deleted successfully"}


@router.get("/me/stats")
async def get_user_stats(current_user: User = Depends(get_current_user)):
    """Get user statistics"""
    
    # This would typically query related data
    # For now, return basic stats
    return {
        "total_agents": len(current_user.agents),
        "active_agents": len([agent for agent in current_user.agents if agent.status == "active"]),
        "total_usage": sum(agent.usage_count for agent in current_user.agents),
        "avg_success_rate": sum(agent.success_rate for agent in current_user.agents) / max(len(current_user.agents), 1)
    }