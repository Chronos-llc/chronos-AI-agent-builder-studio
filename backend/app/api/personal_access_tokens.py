from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from datetime import datetime
import json

from app.models.personal_access_token import PersonalAccessToken as PersonalAccessTokenModel
from app.models.user import User as UserModel
from app.schemas.personal_access_token import (
    PersonalAccessTokenCreate,
    PersonalAccessTokenResponse,
    PersonalAccessTokenWithToken,
    PersonalAccessTokenUpdate,
    PersonalAccessTokenList
)
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.post("/tokens/", response_model=PersonalAccessTokenWithToken, status_code=status.HTTP_201_CREATED)
async def create_personal_access_token(
    token_data: PersonalAccessTokenCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new personal access token"""
    # Generate the token
    token = PersonalAccessTokenModel.generate_token()
    token_hash = PersonalAccessTokenModel.hash_token(token)
    token_prefix = PersonalAccessTokenModel.get_token_prefix(token)
    
    # Convert scopes list to JSON string
    scopes_json = json.dumps(token_data.scopes) if token_data.scopes else None
    
    # Create the token record
    db_token = PersonalAccessTokenModel(
        name=token_data.name,
        token_hash=token_hash,
        token_prefix=token_prefix,
        user_id=current_user.id,
        scopes=scopes_json,
        expires_at=token_data.expires_at,
        is_active=True,
        is_revoked=False,
        usage_count=0
    )
    
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    
    # Return the response with the full token (only time it's shown)
    response_data = PersonalAccessTokenResponse.from_orm(db_token).dict()
    response_data['token'] = token
    
    return PersonalAccessTokenWithToken(**response_data)


@router.get("/tokens/", response_model=PersonalAccessTokenList)
async def list_personal_access_tokens(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """List all personal access tokens for the current user"""
    result = await db.execute(
        select(PersonalAccessTokenModel).where(
            PersonalAccessTokenModel.user_id == current_user.id
        ).order_by(PersonalAccessTokenModel.created_at.desc())
    )
    tokens = result.scalars().all()
    
    return PersonalAccessTokenList(
        tokens=[PersonalAccessTokenResponse.from_orm(token) for token in tokens],
        total=len(tokens)
    )


@router.get("/tokens/{token_id}", response_model=PersonalAccessTokenResponse)
async def get_personal_access_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get a specific personal access token"""
    result = await db.execute(
        select(PersonalAccessTokenModel).where(
            PersonalAccessTokenModel.id == token_id,
            PersonalAccessTokenModel.user_id == current_user.id
        )
    )
    token = result.scalars().first()
    
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return PersonalAccessTokenResponse.from_orm(token)


@router.put("/tokens/{token_id}", response_model=PersonalAccessTokenResponse)
async def update_personal_access_token(
    token_id: int,
    token_update: PersonalAccessTokenUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update a personal access token"""
    result = await db.execute(
        select(PersonalAccessTokenModel).where(
            PersonalAccessTokenModel.id == token_id,
            PersonalAccessTokenModel.user_id == current_user.id
        )
    )
    db_token = result.scalars().first()
    
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # Update fields
    for key, value in token_update.dict(exclude_unset=True).items():
        setattr(db_token, key, value)
    
    await db.commit()
    await db.refresh(db_token)
    
    return PersonalAccessTokenResponse.from_orm(db_token)


@router.post("/tokens/{token_id}/revoke", response_model=PersonalAccessTokenResponse)
async def revoke_personal_access_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Revoke a personal access token"""
    result = await db.execute(
        select(PersonalAccessTokenModel).where(
            PersonalAccessTokenModel.id == token_id,
            PersonalAccessTokenModel.user_id == current_user.id
        )
    )
    db_token = result.scalars().first()
    
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    db_token.is_revoked = True
    db_token.is_active = False
    
    await db.commit()
    await db.refresh(db_token)
    
    return PersonalAccessTokenResponse.from_orm(db_token)


@router.delete("/tokens/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_personal_access_token(
    token_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Delete a personal access token"""
    result = await db.execute(
        select(PersonalAccessTokenModel).where(
            PersonalAccessTokenModel.id == token_id,
            PersonalAccessTokenModel.user_id == current_user.id
        )
    )
    db_token = result.scalars().first()
    
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    await db.delete(db_token)
    await db.commit()
