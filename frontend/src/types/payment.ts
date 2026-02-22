/**
 * Payment Methods Types
 * Based on backend/app/schemas/payment_methods.py
 */

// Payment Provider Enum
export enum PaymentProvider {
  STRIPE = "stripe",
  PAYPAL = "paypal",
  BANK = "bank",
  CREDIT_CARD = "credit_card",
  CRYPTO = "crypto",
}

// Payment Method Base Type
export interface PaymentMethodBase {
  name: string;
  provider: PaymentProvider;
  is_active: boolean;
  configuration?: Record<string, any>;
}

// Payment Method Create Type
export type PaymentMethodCreate = PaymentMethodBase;

// Payment Method Update Type
export interface PaymentMethodUpdate {
  name?: string;
  is_active?: boolean;
  configuration?: Record<string, any>;
}

// Payment Method Response Type
export interface PaymentMethodResponse extends PaymentMethodBase {
  id: number;
  created_at: string;
  updated_at: string;
}

// Payment Method List Type (paginated results)
export interface PaymentMethodList {
  items: PaymentMethodResponse[];
  total: number;
  page: number;
  page_size: number;
}

// Payment Settings Base Type
export interface PaymentSettingsBase {
  currency: string;
  tax_rate: number;
  default_payment_method_id?: number;
  settings?: Record<string, any>;
}

// Payment Settings Update Type
export interface PaymentSettingsUpdate {
  currency?: string;
  tax_rate?: number;
  default_payment_method_id?: number;
  settings?: Record<string, any>;
}

// Payment Settings Response Type
export interface PaymentSettingsResponse extends PaymentSettingsBase {
  id: number;
  updated_at: string;
}

// Payment Transaction Base Type
export interface PaymentTransactionBase {
  user_id: number;
  amount: number;
  currency: string;
  payment_method_id: number;
  transaction_type: string;
  status: string;
  metadata?: Record<string, any>;
}

// Payment Transaction Create Type
export type PaymentTransactionCreate = PaymentTransactionBase;

// Payment Transaction Response Type
export interface PaymentTransactionResponse extends PaymentTransactionBase {
  id: number;
  created_at: string;
  updated_at: string;
}

// Payment Transaction List Type (paginated results)
export interface PaymentTransactionList {
  items: PaymentTransactionResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface PaymentStats {
  active_methods: number;
  inactive_methods: number;
  by_provider: Record<string, number>;
  total_revenue?: number;
}

export interface UserBalanceAccount {
  id: number
  user_id: number
  currency: string
  balance: number
  updated_at: string
}

export interface UserBalanceTransaction {
  id: number
  user_id: number
  currency: string
  amount_delta: number
  reason: string
  admin_user_id?: number | null
  additional_metadata?: Record<string, unknown> | null
  created_at: string
}

export interface UserBalanceSummary {
  user_id: number
  balances: UserBalanceAccount[]
  transactions: UserBalanceTransaction[]
}

export interface UserBalanceUserListItem {
  user_id: number
  username: string
  email: string
  balances: Record<string, number>
}

export interface UserBalanceUsersResponse {
  items: UserBalanceUserListItem[]
  total: number
}

export interface UserBalanceAdjustPayload {
  currency: string
  amount_delta: number
  reason: string
  metadata?: Record<string, unknown>
}

// Export all types
export type PaymentMethod = PaymentMethodResponse;
export type PaymentSettings = PaymentSettingsResponse;
export type PaymentTransaction = PaymentTransactionResponse;
