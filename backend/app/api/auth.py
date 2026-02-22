from datetime import timedelta, datetime
import json
import re
import secrets
from urllib.parse import urlencode
from typing import Optional, Literal, Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token,
    verify_refresh_token,
    verify_password_reset_token,
    generate_password_reset_token
)
from app.core.redis import blacklist_token, is_token_blacklisted, get_redis_client
from app.models.user import User
from app.models.social_account import SocialAccount
from app.models.admin import AdminUser, AdminAuditLog
from app.schemas.auth import (
    UserCreate, UserLogin, UserResponse, Token,
    PasswordReset, PasswordResetConfirm, PasswordChange, SessionContextResponse
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
OAuthProvider = Literal["google", "github"]
OAUTH_STATE_TTL_MINUTES = 10


def _sanitize_return_to(return_to: Optional[str]) -> str:
    if not return_to or not return_to.startswith("/"):
        return "/app"
    if return_to.startswith("//"):
        return "/app"
    return return_to


def _get_oauth_provider_config(provider: OAuthProvider) -> dict[str, Any]:
    if provider == "google":
        if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET or not settings.GOOGLE_OAUTH_REDIRECT_URI:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google OAuth is not configured")
        return {
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
            "scope": "openid email profile",
        }
    if provider == "github":
        if not settings.GITHUB_OAUTH_CLIENT_ID or not settings.GITHUB_OAUTH_CLIENT_SECRET or not settings.GITHUB_OAUTH_REDIRECT_URI:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GitHub OAuth is not configured")
        return {
            "client_id": settings.GITHUB_OAUTH_CLIENT_ID,
            "client_secret": settings.GITHUB_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GITHUB_OAUTH_REDIRECT_URI,
            "authorize_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "emails_url": "https://api.github.com/user/emails",
            "scope": "read:user user:email",
        }
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported OAuth provider")


def _build_oauth_state(provider: OAuthProvider, return_to: Optional[str]) -> str:
    payload = {
        "type": "oauth_state",
        "provider": provider,
        "return_to": _sanitize_return_to(return_to),
        "nonce": secrets.token_urlsafe(16),
        "exp": datetime.utcnow() + timedelta(minutes=OAUTH_STATE_TTL_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _verify_oauth_state(state: str, provider: OAuthProvider) -> dict[str, Any]:
    try:
        payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OAuth state")
    if payload.get("type") != "oauth_state" or payload.get("provider") != provider:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OAuth state")
    return payload


def _normalize_username_seed(seed: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9_]+", "_", seed).strip("_").lower()
    if len(sanitized) < 3:
        return "user"
    return sanitized[:40]


async def _generate_unique_username(db: AsyncSession, seed: str) -> str:
    base = _normalize_username_seed(seed)
    candidate = base
    counter = 1
    while True:
        result = await db.execute(select(User).where(User.username == candidate))
        existing = result.scalar_one_or_none()
        if not existing:
            return candidate
        candidate = f"{base}_{counter}"
        counter += 1


async def _exchange_code_for_access_token(provider: OAuthProvider, code: str) -> str:
    config = _get_oauth_provider_config(provider)
    async with httpx.AsyncClient(timeout=15.0) as client:
        if provider == "google":
            response = await client.post(
                config["token_url"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "redirect_uri": config["redirect_uri"],
                },
            )
        else:
            response = await client.post(
                config["token_url"],
                data={
                    "code": code,
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "redirect_uri": config["redirect_uri"],
                },
                headers={"Accept": "application/json"},
            )
    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"{provider.capitalize()} token exchange failed")
    access_token = response.json().get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"{provider.capitalize()} token exchange failed")
    return access_token


async def _fetch_oauth_identity(provider: OAuthProvider, access_token: str) -> dict[str, Any]:
    config = _get_oauth_provider_config(provider)
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        if provider == "google":
            response = await client.get(config["userinfo_url"], headers=headers)
            if response.status_code >= 400:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to fetch Google profile")
            data = response.json()
            provider_user_id = data.get("sub")
            email = data.get("email")
            if not provider_user_id or not email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account is missing required profile data")
            return {
                "provider_user_id": str(provider_user_id),
                "email": email.lower(),
                "email_verified": bool(data.get("email_verified")),
                "full_name": data.get("name") or email.split("@")[0],
            }

        user_response = await client.get(config["userinfo_url"], headers=headers)
        if user_response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to fetch GitHub profile")
        user_data = user_response.json()

        emails_response = await client.get(config["emails_url"], headers=headers)
        if emails_response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to read GitHub email. Grant user:email scope.")
        email_records = emails_response.json()
        verified_emails = [item for item in email_records if item.get("verified") and item.get("email")]
        primary_verified = next((item for item in verified_emails if item.get("primary")), None)
        selected = primary_verified or (verified_emails[0] if verified_emails else None)
        if not selected:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GitHub account must have at least one verified email")
        return {
            "provider_user_id": str(user_data.get("id")),
            "email": selected["email"].lower(),
            "email_verified": True,
            "full_name": user_data.get("name") or user_data.get("login") or selected["email"].split("@")[0],
        }


async def _upsert_oauth_user(
    db: AsyncSession,
    provider: OAuthProvider,
    provider_user_id: str,
    email: str,
    email_verified: bool,
    full_name: str,
) -> User:
    existing_social = await db.execute(
        select(SocialAccount).where(
            SocialAccount.provider == provider,
            SocialAccount.provider_user_id == provider_user_id,
        )
    )
    social_account = existing_social.scalar_one_or_none()
    if social_account:
        user_result = await db.execute(select(User).where(User.id == social_account.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            return user

    user_result = await db.execute(select(User).where(User.email == email))
    user = user_result.scalar_one_or_none()
    if not user:
        username_seed = email.split("@")[0] if email else full_name
        username = await _generate_unique_username(db, username_seed)
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            is_active=True,
            is_verified=email_verified,
        )
        db.add(user)
        await db.flush()
    elif email_verified and not user.is_verified:
        user.is_verified = True

    if not social_account:
        social_account = SocialAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=email,
        )
        db.add(social_account)

    await db.commit()
    await db.refresh(user)
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis_client = Depends(get_redis_client)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        if not payload or payload.get("type") != "access":
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Check if token is blacklisted
    jti = payload.get("jti", "")
    if jti and await is_token_blacklisted(jti):
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def _get_active_admin_profile_for_user(db: AsyncSession, user_id: int) -> AdminUser | None:
    result = await db.execute(
        select(AdminUser).where(
            AdminUser.user_id == user_id,
            AdminUser.is_active == True,
        )
    )
    return result.scalar_one_or_none()


@router.get("/oauth/{provider}/start")
async def oauth_start(provider: str, return_to: Optional[str] = "/app"):
    normalized_provider = provider.lower()
    if normalized_provider not in {"google", "github"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported OAuth provider")

    oauth_provider: OAuthProvider = normalized_provider  # type: ignore[assignment]
    config = _get_oauth_provider_config(oauth_provider)
    state = _build_oauth_state(oauth_provider, return_to)

    if oauth_provider == "google":
        params = {
            "response_type": "code",
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "scope": config["scope"],
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
    else:
        params = {
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "scope": config["scope"],
            "state": state,
            "allow_signup": "true",
        }

    redirect_url = f"{config['authorize_url']}?{urlencode(params)}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    normalized_provider = provider.lower()
    if normalized_provider not in {"google", "github"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported OAuth provider")
    if not code or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing OAuth callback parameters")

    oauth_provider: OAuthProvider = normalized_provider  # type: ignore[assignment]
    state_payload = _verify_oauth_state(state, oauth_provider)
    access_token = await _exchange_code_for_access_token(oauth_provider, code)
    identity = await _fetch_oauth_identity(oauth_provider, access_token)

    user = await _upsert_oauth_user(
        db=db,
        provider=oauth_provider,
        provider_user_id=identity["provider_user_id"],
        email=identity["email"],
        email_verified=identity["email_verified"],
        full_name=identity["full_name"],
    )

    chronos_access_token = create_access_token(subject=user.id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    chronos_refresh_token = create_refresh_token(subject=user.id)

    return_to = _sanitize_return_to(state_payload.get("return_to"))
    frontend_base = settings.FRONTEND_BASE_URL.rstrip("/")
    response = RedirectResponse(url=f"{frontend_base}{return_to}", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=chronos_access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=chronos_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return response


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    result = await db.execute(
        select(User).where((User.email == user_data.email) | (User.username == user_data.username))
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Verify password confirmation
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login user and return tokens"""
    
    # Find user by email (form_data.username contains email)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    # Set tokens as HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token cookie"""
    
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    additional_claims: dict[str, Any] = {}
    if payload.get("is_impersonation"):
        additional_claims = {
            "is_impersonation": True,
            "impersonator_user_id": payload.get("impersonator_user_id"),
            "impersonator_admin_user_id": payload.get("impersonator_admin_user_id"),
        }

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims=additional_claims or None,
    )
    new_refresh_token = create_refresh_token(
        subject=user.id,
        additional_claims=additional_claims or None,
    )
    
    # Set new tokens as cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    redis_client = Depends(get_redis_client)
):
    """Logout user (blacklist current token and clear cookies)"""
    # Verify and decode token
    payload = verify_token(token)
    if payload:
        jti = payload.get("jti")
        if jti:
            # Blacklist token until expiration
            expire = payload["exp"] - datetime.utcnow().timestamp()
            await blacklist_token(jti, int(expire))
    
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/session-context", response_model=SessionContextResponse)
async def get_session_context(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    payload = verify_token(token) or {}
    is_impersonating = bool(payload.get("is_impersonation"))
    impersonator_user_id = payload.get("impersonator_user_id")
    impersonator_admin_user_id = payload.get("impersonator_admin_user_id")

    active_admin = await _get_active_admin_profile_for_user(db, current_user.id)
    return SessionContextResponse(
        user=current_user,
        is_admin=(bool(active_admin) or bool(current_user.is_superuser)) and not is_impersonating,
        is_impersonating=is_impersonating,
        impersonator_user_id=int(impersonator_user_id) if impersonator_user_id is not None else None,
        impersonator_admin_user_id=int(impersonator_admin_user_id) if impersonator_admin_user_id is not None else None,
    )


@router.post("/impersonation/exit", response_model=Token)
async def exit_impersonation(
    response: Response,
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    payload = verify_token(token)
    if not payload or payload.get("type") != "access" or not payload.get("is_impersonation"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impersonation session required",
        )

    impersonator_user_id = payload.get("impersonator_user_id")
    impersonator_admin_user_id = payload.get("impersonator_admin_user_id")
    if not impersonator_user_id or not impersonator_admin_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid impersonation token",
        )

    user_result = await db.execute(select(User).where(User.id == int(impersonator_user_id)))
    impersonator_user = user_result.scalar_one_or_none()
    if not impersonator_user or not impersonator_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impersonator account is invalid",
        )

    admin_result = await db.execute(
        select(AdminUser).where(
            and_(
                AdminUser.id == int(impersonator_admin_user_id),
                AdminUser.user_id == impersonator_user.id,
                AdminUser.is_active == True,
            )
        )
    )
    admin_profile = admin_result.scalar_one_or_none()
    if not admin_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impersonator no longer has admin access",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    restored_access_token = create_access_token(
        subject=impersonator_user.id,
        expires_delta=access_token_expires,
    )
    restored_refresh_token = create_refresh_token(subject=impersonator_user.id)

    response.set_cookie(
        key="access_token",
        value=restored_access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=restored_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    db.add(
        AdminAuditLog(
            admin_user_id=admin_profile.id,
            action="switch_profile_exit",
            resource_type="user",
            resource_id=int(payload.get("sub")),
            details=json.dumps(
                {
                    "impersonated_user_id": int(payload.get("sub")),
                    "restored_admin_user_id": impersonator_user.id,
                }
            ),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            status="success",
        )
    )
    await db.commit()

    return {
        "access_token": restored_access_token,
        "refresh_token": restored_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/password-reset")
async def request_password_reset(data: PasswordReset):
    """Request password reset"""
    # In a real implementation, you would send an email here
    # For now, we'll just return success
    return {"message": "Password reset email sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    """Confirm password reset with token"""
    
    email = verify_password_reset_token(data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    if data.new_password != data.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = get_password_hash(data.new_password)
    await db.commit()
    
    return {"message": "Password successfully updated"}


@router.post("/password-change")
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change password for current user"""
    
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    if data.new_password != data.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(data.new_password)
    await db.commit()
    
    return {"message": "Password successfully updated"}
