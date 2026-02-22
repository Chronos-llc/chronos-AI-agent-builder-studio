from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK = "bank"
    CREDIT_CARD = "credit_card"
    CRYPTO = "crypto"


class PaymentMethodBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    provider: PaymentProvider
    is_active: bool = True
    configuration: Optional[Dict[str, Any]] = None


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    configuration: Optional[Dict[str, Any]] = None


class PaymentMethodResponse(PaymentMethodBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentMethodList(BaseModel):
    items: List[PaymentMethodResponse]
    total: int
    page: int
    page_size: int


class PaymentSettingsBase(BaseModel):
    currency: str = Field(..., min_length=3, max_length=3)
    tax_rate: float = Field(..., ge=0, le=100)
    default_payment_method_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None


class PaymentSettingsUpdate(BaseModel):
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    tax_rate: Optional[float] = Field(None, ge=0, le=100)
    default_payment_method_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None


class PaymentSettingsResponse(PaymentSettingsBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentTransactionBase(BaseModel):
    user_id: int
    amount: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    payment_method_id: int
    transaction_type: str = Field(..., min_length=1, max_length=50)  # e.g., SUBSCRIPTION, ONE_TIME, REFUND
    status: str = Field(..., min_length=1, max_length=20)  # e.g., PENDING, COMPLETED, FAILED, REFUNDED
    metadata: Optional[Dict[str, Any]] = None


class PaymentTransactionCreate(PaymentTransactionBase):
    pass


class PaymentTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    amount: float
    currency: str
    payment_method_id: int
    transaction_type: str
    status: str
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="additional_metadata")
    id: int
    created_at: datetime
    updated_at: datetime


class PaymentTransactionList(BaseModel):
    items: List[PaymentTransactionResponse]
    total: int
    page: int
    page_size: int


class UserBalanceAccountResponse(BaseModel):
    id: int
    user_id: int
    currency: str
    balance: float
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBalanceTransactionResponse(BaseModel):
    id: int
    user_id: int
    currency: str
    amount_delta: float
    reason: str
    admin_user_id: Optional[int] = None
    additional_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserBalanceSummaryResponse(BaseModel):
    user_id: int
    balances: List[UserBalanceAccountResponse]
    transactions: List[UserBalanceTransactionResponse]


class UserBalanceAdjustRequest(BaseModel):
    currency: str = Field(..., min_length=3, max_length=3)
    amount_delta: float = Field(..., ne=0)
    reason: str = Field(..., min_length=2, max_length=255)
    metadata: Optional[Dict[str, Any]] = None


class UserBalanceUserListItem(BaseModel):
    user_id: int
    username: str
    email: str
    balances: Dict[str, float]


class UserBalanceUsersResponse(BaseModel):
    items: List[UserBalanceUserListItem]
    total: int
