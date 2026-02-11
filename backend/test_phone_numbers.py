import pytest
from pydantic import ValidationError

from app.core.config import settings
from app.core.phone_providers import PhoneProviderManager, TwilioProvider, VonageProvider
from app.schemas.phone_number import PhoneNumberPurchaseRequest, PhoneNumberProvider


def test_purchase_requires_confirmation():
    with pytest.raises(ValidationError):
        PhoneNumberPurchaseRequest(
            country_code="US",
            phone_number_e164="+14155550100",
            capabilities=["voice"],
            confirm_purchase=False,
        )


def test_purchase_accepts_confirmation_true():
    payload = PhoneNumberPurchaseRequest(
        country_code="US",
        phone_number_e164="+14155550100",
        capabilities=["voice"],
        confirm_purchase=True,
    )
    assert payload.confirm_purchase is True
    assert payload.country_code == "US"


def test_provider_configuration_detection(monkeypatch):
    monkeypatch.setattr(settings, "TWILIO_ACCOUNT_SID", None, raising=False)
    monkeypatch.setattr(settings, "TWILIO_API_KEY", None, raising=False)
    monkeypatch.setattr(settings, "TWILIO_API_SECRET", None, raising=False)
    monkeypatch.setattr(settings, "VONAGE_API_KEY", None, raising=False)
    monkeypatch.setattr(settings, "VONAGE_API_SECRET", None, raising=False)

    manager = PhoneProviderManager()
    availability = {item["provider"]: item for item in manager.availability()}

    assert availability[PhoneNumberProvider.TWILIO]["configured"] is False
    assert availability[PhoneNumberProvider.VONAGE]["configured"] is False


def test_provider_configured_when_keys_present(monkeypatch):
    monkeypatch.setattr(settings, "TWILIO_ACCOUNT_SID", "AC123", raising=False)
    monkeypatch.setattr(settings, "TWILIO_API_KEY", "SK123", raising=False)
    monkeypatch.setattr(settings, "TWILIO_API_SECRET", "secret", raising=False)
    monkeypatch.setattr(settings, "VONAGE_API_KEY", "key", raising=False)
    monkeypatch.setattr(settings, "VONAGE_API_SECRET", "secret", raising=False)

    assert TwilioProvider().configured() is True
    assert VonageProvider().configured() is True

