from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.user_profile import UserProfile, UserPersona
from app.schemas.user_profile import UserOnboardingRequest, UserProfileResponse, UserProfileUpdate

router = APIRouter()


async def _get_or_create_profile(db: AsyncSession, user_id: int) -> UserProfile:
    profile = (
        await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    ).scalar_one_or_none()
    if profile:
        return profile

    profile = UserProfile(user_id=user_id, onboarding_completed=False)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


def _validate_onboarding(request: UserOnboardingRequest) -> None:
    persona = request.persona
    if persona == UserPersona.DEVELOPER.value and not request.github_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="github_url is required for developer persona",
        )
    if persona in {UserPersona.POWER_USER.value, UserPersona.ENTERPRISE.value} and not request.linkedin_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="linkedin_url is required for power_user and enterprise personas",
        )


@router.get("/users/me/profile", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_or_create_profile(db, current_user.id)


@router.put("/users/me/profile", response_model=UserProfileResponse)
async def update_my_profile(
    update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(db, current_user.id)
    data = update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.post("/users/me/onboarding", response_model=UserProfileResponse)
async def complete_onboarding(
    request: UserOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _validate_onboarding(request)
    profile = await _get_or_create_profile(db, current_user.id)
    data = request.model_dump()
    for field, value in data.items():
        setattr(profile, field, value)
    profile.onboarding_completed = True

    await db.commit()
    await db.refresh(profile)
    return profile

