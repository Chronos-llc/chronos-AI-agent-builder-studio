from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc, update
from sqlalchemy.orm import joinedload
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.user import User
from app.models.admin import AdminUser
from app.models.payment_methods import PaymentMethod, PaymentSettings, PaymentTransaction
from app.models.usage import UserBalanceAccount, UserBalanceTransaction
from app.api.auth import get_current_user
from app.schemas.payment_methods import (
    PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodResponse, PaymentMethodList,
    PaymentSettingsUpdate, PaymentSettingsResponse, PaymentTransactionBase, PaymentTransactionResponse, PaymentTransactionList,
    UserBalanceAdjustRequest, UserBalanceAccountResponse, UserBalanceSummaryResponse, UserBalanceTransactionResponse,
    UserBalanceUserListItem, UserBalanceUsersResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# ISO 4217 currency codes commonly used
VALID_CURRENCIES = {
    "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "MXN",
    "BRL", "KRW", "SGD", "HKD", "NOK", "SEK", "DKK", "NZD", "ZAR", "RUB",
    "TRY", "PLN", "THB", "IDR", "MYR", "PHP", "CZK", "ILS", "CLP", "PKR",
    "EGP", "TWD", "AED", "SAR", "VND", "NGN", "BDT", "QAR", "KWD", "COP",
}


async def is_admin(user: User, db: AsyncSession) -> bool:
    """Check whether user has effective admin access."""
    if user.is_superuser:
        return True
    result = await db.execute(
        select(AdminUser).where(
            and_(
                AdminUser.user_id == user.id,
                AdminUser.is_active == True,
            )
        )
    )
    return result.scalar_one_or_none() is not None


# Payment Methods Endpoints
@router.get("/methods", response_model=PaymentMethodList)
async def get_payment_methods(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: str = Query("name", description="Sort field: name, provider, created_at"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment methods"""
    
    admin_access = await is_admin(current_user, db)
    if not admin_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    query = select(PaymentMethod)
    
    if provider:
        query = query.where(PaymentMethod.provider == provider)
    
    if is_active is not None:
        query = query.where(PaymentMethod.is_active == is_active)
    
    # Sorting
    sort_field = PaymentMethod.name
    if sort_by == "provider":
        sort_field = PaymentMethod.provider
    elif sort_by == "created_at":
        sort_field = PaymentMethod.created_at
    
    if sort_order == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))
    
    # Pagination
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    methods = result.scalars().all()
    
    return {
        "items": [PaymentMethodResponse.from_orm(method) for method in methods],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/methods/{method_id}", response_model=PaymentMethodResponse)
async def get_payment_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific payment method"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == method_id))
    method = result.scalar_one_or_none()
    
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    return PaymentMethodResponse.from_orm(method)


@router.post("/methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_method(
    method_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new payment method (admin only)"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if method with same name already exists
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.name == method_data.name))
    existing_method = result.scalar_one_or_none()
    
    if existing_method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method with this name already exists"
        )
    
    method = PaymentMethod(**method_data.dict())
    db.add(method)
    await db.commit()
    await db.refresh(method)
    
    return PaymentMethodResponse.from_orm(method)


@router.put("/methods/{method_id}", response_model=PaymentMethodResponse)
async def update_payment_method(
    method_id: int,
    method_update: PaymentMethodUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update payment method (admin only)"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == method_id))
    method = result.scalar_one_or_none()
    
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    # Update fields
    update_data = method_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(method, field, value)
    
    await db.commit()
    await db.refresh(method)
    
    return PaymentMethodResponse.from_orm(method)


@router.delete("/methods/{method_id}")
async def delete_payment_method(
    method_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete payment method (admin only)"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == method_id))
    method = result.scalar_one_or_none()
    
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    await db.delete(method)
    await db.commit()
    
    return {"message": "Payment method deleted successfully"}


# Payment Settings Endpoints
@router.get("/settings", response_model=PaymentSettingsResponse)
async def get_payment_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment settings"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get or create default settings
    result = await db.execute(select(PaymentSettings))
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create default settings
        settings = PaymentSettings(
            currency="USD",
            tax_rate=0.0,
            settings={}
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return PaymentSettingsResponse.from_orm(settings)


@router.put("/settings", response_model=PaymentSettingsResponse)
async def update_payment_settings(
    settings_update: PaymentSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update payment settings (admin only)"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(PaymentSettings))
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment settings not found"
        )
    
    # Update fields
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    settings.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(settings)
    
    return PaymentSettingsResponse.from_orm(settings)


# Payment Transactions Endpoints
@router.get("/transactions", response_model=PaymentTransactionList)
async def get_payment_transactions(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    method_id: Optional[int] = Query(None, description="Filter by payment method ID"),
    status: Optional[str] = Query(None, description="Filter by transaction status"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    sort_by: str = Query("created_at", description="Sort field: created_at, amount, status"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment transactions"""
    
    admin_access = await is_admin(current_user, db)
    if not admin_access:
        # Non-admins can only see their own transactions
        user_id = current_user.id
    
    query = select(PaymentTransaction)
    
    if user_id:
        query = query.where(PaymentTransaction.user_id == user_id)
    
    if method_id:
        query = query.where(PaymentTransaction.payment_method_id == method_id)
    
    if status:
        query = query.where(PaymentTransaction.status == status)
    
    if transaction_type:
        query = query.where(PaymentTransaction.transaction_type == transaction_type)
    
    # Sorting
    sort_field = PaymentTransaction.created_at
    if sort_by == "amount":
        sort_field = PaymentTransaction.amount
    elif sort_by == "status":
        sort_field = PaymentTransaction.status
    
    if sort_order == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))
    
    # Pagination
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return {
        "items": [PaymentTransactionResponse.from_orm(tx) for tx in transactions],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/transactions", response_model=PaymentTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_transaction(
    transaction_data: PaymentTransactionBase,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new payment transaction"""
    
    admin_access = await is_admin(current_user, db)
    if not admin_access and transaction_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create transactions for yourself"
        )
    
    # Validate payment method exists
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == transaction_data.payment_method_id))
    method = result.scalar_one_or_none()
    
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    if not method.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method is not active"
        )
    
    # Create transaction record
    transaction = PaymentTransaction(
        user_id=transaction_data.user_id,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        payment_method_id=transaction_data.payment_method_id,
        transaction_type=transaction_data.transaction_type,
        status=transaction_data.status,
        additional_metadata=transaction_data.metadata,
        external_transaction_id=transaction_data.metadata.get("external_id") if transaction_data.metadata else None
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return PaymentTransactionResponse.from_orm(transaction)


@router.get("/stats", response_model=Dict[str, Any])
async def get_payment_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment statistics"""
    
    if not await is_admin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Count active/inactive methods
    active_count = await db.execute(select(func.count()).where(PaymentMethod.is_active == True))
    active_count = active_count.scalar_one()
    
    inactive_count = await db.execute(select(func.count()).where(PaymentMethod.is_active == False))
    inactive_count = inactive_count.scalar_one()
    
    # Count by provider
    provider_stats = {}
    providers = ["stripe", "paypal", "bank", "credit_card", "crypto"]
    for provider in providers:
        count = await db.execute(select(func.count()).where(PaymentMethod.provider == provider))
        provider_stats[provider] = count.scalar_one()
    
    return {
        "active_methods": active_count,
        "inactive_methods": inactive_count,
        "by_provider": provider_stats
    }


@router.get("/balances/users", response_model=UserBalanceUsersResponse)
async def list_user_balances(
    query: Optional[str] = Query(None, description="Search by email or username"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not await is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    users_query = select(User)
    if query:
        pattern = f"%{query}%"
        users_query = users_query.where(or_(User.email.ilike(pattern), User.username.ilike(pattern)))

    total = int((await db.execute(select(func.count()).select_from(users_query.subquery()))).scalar_one() or 0)
    users = (
        await db.execute(
            users_query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
    ).scalars().all()

    rows: list[UserBalanceUserListItem] = []
    for user in users:
        balances = (
            await db.execute(select(UserBalanceAccount).where(UserBalanceAccount.user_id == user.id))
        ).scalars().all()
        rows.append(
            UserBalanceUserListItem(
                user_id=user.id,
                username=user.username,
                email=user.email,
                balances={balance.currency: float(balance.balance or 0) for balance in balances},
            )
        )

    return UserBalanceUsersResponse(items=rows, total=total)


@router.get("/balances/users/{user_id}", response_model=UserBalanceSummaryResponse)
async def get_user_balance_summary(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not await is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    target_user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    balances = (
        await db.execute(select(UserBalanceAccount).where(UserBalanceAccount.user_id == user_id))
    ).scalars().all()
    transactions = (
        await db.execute(
            select(UserBalanceTransaction)
            .where(UserBalanceTransaction.user_id == user_id)
            .order_by(UserBalanceTransaction.created_at.desc())
            .limit(100)
        )
    ).scalars().all()

    return UserBalanceSummaryResponse(
        user_id=user_id,
        balances=[
            UserBalanceAccountResponse(
                id=balance.id,
                user_id=balance.user_id,
                currency=balance.currency,
                balance=float(balance.balance or 0),
                updated_at=balance.updated_at,
            )
            for balance in balances
        ],
        transactions=[
            UserBalanceTransactionResponse(
                id=tx.id,
                user_id=tx.user_id,
                currency=tx.currency,
                amount_delta=float(tx.amount_delta or 0),
                reason=tx.reason,
                admin_user_id=tx.admin_user_id,
                additional_metadata=tx.additional_metadata,
                created_at=tx.created_at,
            )
            for tx in transactions
        ],
    )


@router.post("/balances/users/{user_id}/adjust", response_model=UserBalanceSummaryResponse)
async def adjust_user_balance(
    user_id: int,
    payload: UserBalanceAdjustRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not await is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    target_user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    currency = payload.currency.upper()
    if currency not in VALID_CURRENCIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid currency code '{currency}'. Supported codes: {', '.join(sorted(VALID_CURRENCIES)[:10])}..."
        )

    # Use FOR UPDATE lock to prevent race conditions in concurrent balance adjustments
    account = (
        await db.execute(
            select(UserBalanceAccount)
            .where(
                and_(UserBalanceAccount.user_id == user_id, UserBalanceAccount.currency == currency)
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if not account:
        account = UserBalanceAccount(user_id=user_id, currency=currency, balance=Decimal("0"))
        db.add(account)
        await db.flush()

    delta = Decimal(str(payload.amount_delta))
    account.balance = (account.balance or Decimal("0")) + delta

    tx = UserBalanceTransaction(
        user_id=user_id,
        currency=currency,
        amount_delta=delta,
        reason=payload.reason,
        admin_user_id=current_user.id,
        additional_metadata=payload.metadata,
    )
    db.add(tx)
    await db.commit()

    balances = (
        await db.execute(select(UserBalanceAccount).where(UserBalanceAccount.user_id == user_id))
    ).scalars().all()
    transactions = (
        await db.execute(
            select(UserBalanceTransaction)
            .where(UserBalanceTransaction.user_id == user_id)
            .order_by(UserBalanceTransaction.created_at.desc())
            .limit(100)
        )
    ).scalars().all()

    return UserBalanceSummaryResponse(
        user_id=user_id,
        balances=[
            UserBalanceAccountResponse(
                id=balance.id,
                user_id=balance.user_id,
                currency=balance.currency,
                balance=float(balance.balance or 0),
                updated_at=balance.updated_at,
            )
            for balance in balances
        ],
        transactions=[
            UserBalanceTransactionResponse(
                id=item.id,
                user_id=item.user_id,
                currency=item.currency,
                amount_delta=float(item.amount_delta or 0),
                reason=item.reason,
                admin_user_id=item.admin_user_id,
                additional_metadata=item.additional_metadata,
                created_at=item.created_at,
            )
            for item in transactions
        ],
    )
