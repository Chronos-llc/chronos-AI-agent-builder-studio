from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.core.phone_providers import (
    PhoneProviderConfigurationError,
    PhoneProviderError,
    phone_provider_manager,
)
from app.models.agent import AgentModel
from app.models.agent_phone_number import AgentPhoneNumber, PhoneNumberProvider
from app.models.user import User
from app.models.voice import VoiceConfiguration
from app.schemas.phone_number import (
    AgentPhoneNumberResponse,
    PhoneNumberOption,
    PhoneNumberPurchaseRequest,
    PhoneNumberSearchRequest,
    PhoneProviderAvailability,
)

router = APIRouter()


async def _get_agent_or_404(agent_id: int, current_user: User, db: AsyncSession) -> AgentModel:
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id,
            )
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


def _to_response(item: AgentPhoneNumber) -> AgentPhoneNumberResponse:
    return AgentPhoneNumberResponse(
        id=item.id,
        agent_id=item.agent_id,
        provider=PhoneNumberProvider(item.provider.value if hasattr(item.provider, "value") else item.provider),
        phone_number_e164=item.phone_number_e164,
        provider_number_id=item.provider_number_id,
        country_code=item.country_code,
        capabilities=item.capabilities or [],
        monthly_cost=item.monthly_cost,
        currency=item.currency,
        is_selected=item.is_selected,
        status=item.status,
        metadata=item.additional_metadata,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/agents/{agent_id}/phone/providers", response_model=List[PhoneProviderAvailability])
async def get_phone_providers(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, current_user, db)
    return [PhoneProviderAvailability(**item) for item in phone_provider_manager.availability()]


@router.post("/agents/{agent_id}/phone/providers/{provider}/search", response_model=List[PhoneNumberOption])
async def search_phone_numbers(
    agent_id: int,
    provider: PhoneNumberProvider,
    payload: PhoneNumberSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, current_user, db)
    provider_client = phone_provider_manager.get(provider)
    try:
        results = await provider_client.search_numbers(
            country_code=payload.country_code,
            capabilities=payload.capabilities,
            limit=payload.limit,
            contains=payload.contains,
        )
        return [PhoneNumberOption(**item) for item in results]
    except PhoneProviderConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except PhoneProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


@router.post("/agents/{agent_id}/phone/providers/{provider}/purchase", response_model=AgentPhoneNumberResponse)
async def purchase_phone_number(
    agent_id: int,
    provider: PhoneNumberProvider,
    payload: PhoneNumberPurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, current_user, db)
    provider_client = phone_provider_manager.get(provider)
    try:
        result = await provider_client.purchase_number(
            country_code=payload.country_code,
            phone_number_e164=payload.phone_number_e164,
            capabilities=payload.capabilities,
            provider_number_id=payload.provider_number_id,
        )
    except PhoneProviderConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except PhoneProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    existing_query = await db.execute(
        select(AgentPhoneNumber).where(
            and_(
                AgentPhoneNumber.agent_id == agent.id,
                AgentPhoneNumber.provider == provider,
                AgentPhoneNumber.phone_number_e164 == result["phone_number_e164"],
            )
        )
    )
    existing = existing_query.scalar_one_or_none()
    if existing:
        return _to_response(existing)

    has_selected_query = await db.execute(
        select(AgentPhoneNumber).where(and_(AgentPhoneNumber.agent_id == agent.id, AgentPhoneNumber.is_selected.is_(True)))
    )
    has_selected = has_selected_query.scalar_one_or_none() is not None

    record = AgentPhoneNumber(
        agent_id=agent.id,
        provider=provider,
        phone_number_e164=result["phone_number_e164"],
        provider_number_id=result["provider_number_id"],
        country_code=result.get("country_code"),
        capabilities=result.get("capabilities", payload.capabilities),
        monthly_cost=result.get("monthly_cost"),
        currency=result.get("currency") or "USD",
        is_selected=not has_selected,
        status="active",
        additional_metadata=result.get("metadata"),
    )
    db.add(record)
    await db.flush()

    if record.is_selected:
        voice_result = await db.execute(select(VoiceConfiguration).where(VoiceConfiguration.agent_id == agent.id))
        voice_config = voice_result.scalar_one_or_none()
        if voice_config:
            voice_config.selected_phone_number_id = record.id
            voice_config.phone_provider_preference = provider

    await db.commit()
    await db.refresh(record)
    return _to_response(record)


@router.get("/agents/{agent_id}/phone/numbers", response_model=List[AgentPhoneNumberResponse])
async def list_agent_phone_numbers(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, current_user, db)
    result = await db.execute(
        select(AgentPhoneNumber).where(AgentPhoneNumber.agent_id == agent_id).order_by(AgentPhoneNumber.created_at.desc())
    )
    items = result.scalars().all()
    return [_to_response(item) for item in items]


@router.post("/agents/{agent_id}/phone/numbers/{number_id}/select", response_model=AgentPhoneNumberResponse)
async def select_agent_phone_number(
    agent_id: int,
    number_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, current_user, db)

    result = await db.execute(
        select(AgentPhoneNumber).where(
            and_(
                AgentPhoneNumber.id == number_id,
                AgentPhoneNumber.agent_id == agent_id,
            )
        )
    )
    selected = result.scalar_one_or_none()
    if not selected:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone number not found")

    all_numbers_result = await db.execute(select(AgentPhoneNumber).where(AgentPhoneNumber.agent_id == agent_id))
    all_numbers = all_numbers_result.scalars().all()
    for item in all_numbers:
        item.is_selected = item.id == selected.id

    voice_result = await db.execute(select(VoiceConfiguration).where(VoiceConfiguration.agent_id == agent_id))
    voice_config = voice_result.scalar_one_or_none()
    if voice_config:
        voice_config.selected_phone_number_id = selected.id
        voice_config.phone_provider_preference = selected.provider

    await db.commit()
    await db.refresh(selected)
    return _to_response(selected)
