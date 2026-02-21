from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.user_profile import FuzzyOnboardingState, UserPersona, UserProfile
from app.schemas.user_profile import (
    UserFuzzyOnboardingRequest,
    UserOnboardingRequest,
    UserOnboardingStatusResponse,
    UserProfileOnboardingRequest,
    UserProfileResponse,
    UserProfileUpdate,
)

router = APIRouter()


async def _get_or_create_profile(db: AsyncSession, user_id: int) -> UserProfile:
    profile = (
        await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    ).scalar_one_or_none()
    if profile:
        if not profile.fuzzy_onboarding_state:
            profile.fuzzy_onboarding_state = FuzzyOnboardingState.PENDING.value
            await db.commit()
            await db.refresh(profile)
        return profile

    profile = UserProfile(
        user_id=user_id,
        onboarding_completed=False,
        fuzzy_onboarding_state=FuzzyOnboardingState.PENDING.value,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


def _validate_profile_onboarding(request: UserProfileOnboardingRequest | UserOnboardingRequest) -> None:
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
    # Use JSON mode so HttpUrl fields are converted to plain strings for DB storage.
    data = update.model_dump(exclude_unset=True, mode="json")
    for field, value in data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.post("/users/me/onboarding/profile", response_model=UserProfileResponse)
async def complete_profile_onboarding(
    request: UserProfileOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _validate_profile_onboarding(request)
    profile = await _get_or_create_profile(db, current_user.id)
    data = request.model_dump(mode="json", exclude_unset=True)
    for field, value in data.items():
        setattr(profile, field, value)
    profile.onboarding_completed = True
    profile.fuzzy_onboarding_state = FuzzyOnboardingState.PENDING.value
    profile.fuzzy_onboarding_completed_at = None
    profile.fuzzy_onboarding_skipped_at = None

    await db.commit()
    await db.refresh(profile)
    return profile


@router.post("/users/me/onboarding/fuzzy", response_model=UserProfileResponse)
async def complete_fuzzy_onboarding(
    request: UserFuzzyOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(db, current_user.id)

    data = request.model_dump(mode="json", exclude_unset=True)
    for field, value in data.items():
        setattr(profile, field, value)
    profile.onboarding_completed = True
    profile.fuzzy_onboarding_state = FuzzyOnboardingState.COMPLETED.value
    profile.fuzzy_onboarding_completed_at = datetime.utcnow()
    profile.fuzzy_onboarding_skipped_at = None

    await db.commit()
    await db.refresh(profile)
    return profile


@router.post("/users/me/onboarding/fuzzy/skip", response_model=UserProfileResponse)
async def skip_fuzzy_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(db, current_user.id)

    # Keep existing completed state if already completed.
    if profile.fuzzy_onboarding_state != FuzzyOnboardingState.COMPLETED.value:
        profile.fuzzy_onboarding_state = FuzzyOnboardingState.SKIPPED.value
        profile.fuzzy_onboarding_skipped_at = datetime.utcnow()
        profile.fuzzy_onboarding_completed_at = None

    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/users/me/onboarding/status", response_model=UserOnboardingStatusResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(db, current_user.id)
    return UserOnboardingStatusResponse(
        onboarding_completed=profile.onboarding_completed,
        fuzzy_onboarding_state=str(profile.fuzzy_onboarding_state),
        fuzzy_onboarding_completed_at=profile.fuzzy_onboarding_completed_at,
        fuzzy_onboarding_skipped_at=profile.fuzzy_onboarding_skipped_at,
        profile=profile,
    )


@router.post("/users/me/onboarding", response_model=UserProfileResponse)
async def complete_onboarding_legacy(
    request: UserOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Backward-compatible endpoint for older clients that submit both profile and fuzzy fields together.
    _validate_profile_onboarding(request)
    profile = await _get_or_create_profile(db, current_user.id)
    data = request.model_dump(mode="json")
    for field, value in data.items():
        setattr(profile, field, value)
    profile.onboarding_completed = True
    profile.fuzzy_onboarding_state = FuzzyOnboardingState.COMPLETED.value
    profile.fuzzy_onboarding_completed_at = datetime.utcnow()
    profile.fuzzy_onboarding_skipped_at = None

    await db.commit()
    await db.refresh(profile)
    return profile
