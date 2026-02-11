from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class PhoneNumberProvider(str, Enum):
    TWILIO = "twilio"
    VONAGE = "vonage"


class PhoneProviderAvailability(BaseModel):
    provider: PhoneNumberProvider
    configured: bool
    available: bool = True
    message: Optional[str] = None


class PhoneNumberSearchRequest(BaseModel):
    country_code: str = Field(default="US", min_length=2, max_length=4)
    capabilities: List[str] = Field(default_factory=lambda: ["voice"])
    limit: int = Field(default=20, ge=1, le=100)
    contains: Optional[str] = Field(default=None, max_length=32)


class PhoneNumberOption(BaseModel):
    provider: PhoneNumberProvider
    provider_number_id: str
    phone_number_e164: str
    country_code: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    monthly_cost: Optional[float] = None
    currency: Optional[str] = "USD"
    metadata: Optional[Dict[str, Any]] = None


class PhoneNumberPurchaseRequest(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=4)
    phone_number_e164: str = Field(..., min_length=5, max_length=32)
    provider_number_id: Optional[str] = None
    capabilities: List[str] = Field(default_factory=lambda: ["voice"])
    confirm_purchase: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_confirmation(self):
        if not self.confirm_purchase:
            raise ValueError("confirm_purchase must be true")
        return self


class AgentPhoneNumberResponse(BaseModel):
    id: int
    agent_id: int
    provider: PhoneNumberProvider
    phone_number_e164: str
    provider_number_id: str
    country_code: Optional[str]
    capabilities: List[str]
    monthly_cost: Optional[float]
    currency: str
    is_selected: bool
    status: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
