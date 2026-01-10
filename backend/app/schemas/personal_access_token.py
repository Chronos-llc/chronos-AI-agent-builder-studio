from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PersonalAccessTokenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name for the token")
    scopes: Optional[List[str]] = Field(default=None, description="List of scopes/permissions")
    expires_at: Optional[str] = Field(default=None, description="Expiration date in ISO format")


class PersonalAccessTokenResponse(BaseModel):
    id: int
    name: str
    token_prefix: str
    scopes: Optional[str]
    last_used_at: Optional[str]
    expires_at: Optional[str]
    is_active: bool
    is_revoked: bool
    usage_count: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class PersonalAccessTokenWithToken(PersonalAccessTokenResponse):
    """Response that includes the full token - only returned on creation"""
    token: str


class PersonalAccessTokenUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class PersonalAccessTokenList(BaseModel):
    tokens: List[PersonalAccessTokenResponse]
    total: int
