from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.models.base import BaseModel


class PaymentMethod(BaseModel):
    """Payment method configuration"""
    __tablename__ = "payment_methods"
    
    name = Column(String(100), nullable=False)  # e.g., "Stripe Credit Card", "PayPal", "Bank Transfer"
    provider = Column(String(50), nullable=False)  # e.g., "stripe", "paypal", "bank"
    is_active = Column(Boolean, server_default='true', nullable=False)
    configuration = Column(JSONB, nullable=True)  # Provider-specific configuration
    
    # Relationships
    payment_settings = relationship("PaymentSettings", back_populates="default_method")
    
    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, name='{self.name}', provider='{self.provider}', active={self.is_active})>"


class PaymentSettings(BaseModel):
    """Global payment settings"""
    __tablename__ = "payment_settings"
    
    currency = Column(String(3), server_default='USD', nullable=False)
    tax_rate = Column(Numeric(precision=5, scale=2), server_default='0.0', nullable=False)
    default_payment_method_id = Column(Integer, ForeignKey("payment_methods.id", ondelete="SET NULL"), nullable=True)
    settings = Column(JSONB, nullable=True)  # Additional payment settings
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    default_method = relationship("PaymentMethod", back_populates="payment_settings")
    
    def __repr__(self):
        return f"<PaymentSettings(id={self.id}, currency='{self.currency}', tax_rate={self.tax_rate})>"


class PaymentTransaction(BaseModel):
    """Payment transaction record"""
    __tablename__ = "payment_transactions"
    
    user_id = Column(Integer, nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    currency = Column(String(3), server_default='USD', nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id", ondelete="SET NULL"), nullable=True)
    transaction_type = Column(String(50), nullable=False)  # e.g., "purchase", "refund", "subscription"
    status = Column(String(50), server_default='pending', nullable=False)  # e.g., "pending", "completed", "failed", "refunded"
    metadata = Column(JSONB, nullable=True)
    external_transaction_id = Column(String(255), nullable=True)  # Transaction ID from payment processor
    
    # Relationships
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    
    def __repr__(self):
        return f"<PaymentTransaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, status='{self.status}')>"


# Add relationship to PaymentMethod
PaymentMethod.transactions = relationship("PaymentTransaction", back_populates="payment_method")