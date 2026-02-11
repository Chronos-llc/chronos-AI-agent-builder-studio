from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.schemas.phone_number import PhoneNumberProvider


class PhoneProviderError(Exception):
    pass


class PhoneProviderConfigurationError(PhoneProviderError):
    pass


class PhoneProviderClient(ABC):
    provider: PhoneNumberProvider

    @abstractmethod
    def configured(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def search_numbers(
        self,
        country_code: str,
        capabilities: List[str],
        limit: int,
        contains: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def purchase_number(
        self,
        country_code: str,
        phone_number_e164: str,
        capabilities: List[str],
        provider_number_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def list_numbers(self, limit: int = 100) -> List[Dict[str, Any]]:
        raise NotImplementedError


def _capability_flags(capabilities: List[str]) -> Dict[str, str]:
    requested = {cap.lower() for cap in capabilities}
    return {
        "voice": "true" if "voice" in requested else "false",
        "sms": "true" if "sms" in requested else "false",
        "mms": "true" if "mms" in requested else "false",
    }


class TwilioProvider(PhoneProviderClient):
    provider = PhoneNumberProvider.TWILIO

    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.api_key = settings.TWILIO_API_KEY
        self.api_secret = settings.TWILIO_API_SECRET
        self.base_url = (
            f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}" if self.account_sid else None
        )

    def configured(self) -> bool:
        return bool(self.account_sid and self.api_key and self.api_secret)

    async def search_numbers(
        self,
        country_code: str,
        capabilities: List[str],
        limit: int,
        contains: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not self.configured():
            raise PhoneProviderConfigurationError("Twilio credentials are not configured")

        flags = _capability_flags(capabilities)
        params = {
            "PageSize": str(limit),
            "VoiceEnabled": flags["voice"],
            "SmsEnabled": flags["sms"],
            "MmsEnabled": flags["mms"],
        }
        if contains:
            params["Contains"] = contains

        url = f"{self.base_url}/AvailablePhoneNumbers/{country_code.upper()}/Local.json"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params=params, auth=(self.api_key or "", self.api_secret or ""))
        if response.status_code >= 400:
            raise PhoneProviderError(f"Twilio search failed: {response.text}")
        payload = response.json()
        results: List[Dict[str, Any]] = []
        for item in payload.get("available_phone_numbers", [])[:limit]:
            results.append(
                {
                    "provider": self.provider,
                    "provider_number_id": item.get("sid") or item.get("phone_number"),
                    "phone_number_e164": item.get("phone_number"),
                    "country_code": item.get("iso_country"),
                    "capabilities": [cap for cap, enabled in (item.get("capabilities") or {}).items() if enabled],
                    "monthly_cost": None,
                    "currency": "USD",
                    "metadata": item,
                }
            )
        return results

    async def purchase_number(
        self,
        country_code: str,
        phone_number_e164: str,
        capabilities: List[str],
        provider_number_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.configured():
            raise PhoneProviderConfigurationError("Twilio credentials are not configured")

        url = f"{self.base_url}/IncomingPhoneNumbers.json"
        data = {"PhoneNumber": phone_number_e164}
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, data=data, auth=(self.api_key or "", self.api_secret or ""))
        if response.status_code >= 400:
            raise PhoneProviderError(f"Twilio purchase failed: {response.text}")
        item = response.json()
        return {
            "provider": self.provider,
            "provider_number_id": item.get("sid") or provider_number_id or phone_number_e164,
            "phone_number_e164": item.get("phone_number") or phone_number_e164,
            "country_code": item.get("iso_country") or country_code.upper(),
            "capabilities": capabilities,
            "monthly_cost": None,
            "currency": "USD",
            "metadata": item,
        }

    async def list_numbers(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.configured():
            raise PhoneProviderConfigurationError("Twilio credentials are not configured")

        url = f"{self.base_url}/IncomingPhoneNumbers.json"
        params = {"PageSize": str(min(limit, 1000))}
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params=params, auth=(self.api_key or "", self.api_secret or ""))
        if response.status_code >= 400:
            raise PhoneProviderError(f"Twilio list numbers failed: {response.text}")
        payload = response.json()
        numbers = payload.get("incoming_phone_numbers", [])
        return [
            {
                "provider": self.provider,
                "provider_number_id": item.get("sid") or item.get("phone_number"),
                "phone_number_e164": item.get("phone_number"),
                "country_code": item.get("iso_country"),
                "capabilities": [],
                "monthly_cost": None,
                "currency": "USD",
                "metadata": item,
            }
            for item in numbers
        ]


class VonageProvider(PhoneProviderClient):
    provider = PhoneNumberProvider.VONAGE

    def __init__(self):
        self.api_key = settings.VONAGE_API_KEY
        self.api_secret = settings.VONAGE_API_SECRET
        self.base_url = "https://rest.nexmo.com"

    def configured(self) -> bool:
        return bool(self.api_key and self.api_secret)

    async def search_numbers(
        self,
        country_code: str,
        capabilities: List[str],
        limit: int,
        contains: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not self.configured():
            raise PhoneProviderConfigurationError("Vonage credentials are not configured")

        params = {
            "api_key": self.api_key or "",
            "api_secret": self.api_secret or "",
            "country": country_code.upper(),
            "size": str(limit),
        }
        if contains:
            params["pattern"] = contains

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{self.base_url}/number/search", params=params)
        if response.status_code >= 400:
            raise PhoneProviderError(f"Vonage search failed: {response.text}")

        payload = response.json()
        results: List[Dict[str, Any]] = []
        for item in payload.get("numbers", [])[:limit]:
            msisdn = item.get("msisdn")
            if not msisdn:
                continue
            e164 = msisdn if msisdn.startswith("+") else f"+{msisdn}"
            results.append(
                {
                    "provider": self.provider,
                    "provider_number_id": msisdn,
                    "phone_number_e164": e164,
                    "country_code": country_code.upper(),
                    "capabilities": capabilities,
                    "monthly_cost": float(item.get("cost")) if item.get("cost") else None,
                    "currency": "USD",
                    "metadata": item,
                }
            )
        return results

    async def purchase_number(
        self,
        country_code: str,
        phone_number_e164: str,
        capabilities: List[str],
        provider_number_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.configured():
            raise PhoneProviderConfigurationError("Vonage credentials are not configured")

        msisdn = provider_number_id or phone_number_e164.lstrip("+")
        data = {
            "api_key": self.api_key or "",
            "api_secret": self.api_secret or "",
            "country": country_code.upper(),
            "msisdn": msisdn,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(f"{self.base_url}/number/buy", data=data)
        if response.status_code >= 400:
            raise PhoneProviderError(f"Vonage purchase failed: {response.text}")
        item = response.json()
        return {
            "provider": self.provider,
            "provider_number_id": msisdn,
            "phone_number_e164": phone_number_e164,
            "country_code": country_code.upper(),
            "capabilities": capabilities,
            "monthly_cost": None,
            "currency": "USD",
            "metadata": item,
        }

    async def list_numbers(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.configured():
            raise PhoneProviderConfigurationError("Vonage credentials are not configured")

        params = {
            "api_key": self.api_key or "",
            "api_secret": self.api_secret or "",
            "size": str(min(limit, 100)),
            "index": "1",
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{self.base_url}/account/numbers", params=params)
        if response.status_code >= 400:
            raise PhoneProviderError(f"Vonage list numbers failed: {response.text}")
        payload = response.json()
        return [
            {
                "provider": self.provider,
                "provider_number_id": item.get("msisdn"),
                "phone_number_e164": f"+{item.get('msisdn')}" if item.get("msisdn") else None,
                "country_code": item.get("country"),
                "capabilities": ["voice", "sms"],
                "monthly_cost": None,
                "currency": "USD",
                "metadata": item,
            }
            for item in payload.get("numbers", [])
            if item.get("msisdn")
        ]


class PhoneProviderManager:
    def __init__(self):
        self._providers = {
            PhoneNumberProvider.TWILIO: TwilioProvider(),
            PhoneNumberProvider.VONAGE: VonageProvider(),
        }

    def get(self, provider: PhoneNumberProvider) -> PhoneProviderClient:
        return self._providers[provider]

    def availability(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for provider_id, provider in self._providers.items():
            configured = provider.configured()
            items.append(
                {
                    "provider": provider_id,
                    "configured": configured,
                    "available": True,
                    "message": None if configured else "Provider credentials missing",
                }
            )
        return items


phone_provider_manager = PhoneProviderManager()
