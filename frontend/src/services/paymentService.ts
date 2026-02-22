/**
 * Payment Methods API Service
 * Handles all payment methods and transactions related API calls
 */

import type {
  PaymentMethod,
  PaymentMethodCreate,
  PaymentMethodUpdate,
  PaymentMethodList,
  PaymentSettings,
  PaymentSettingsUpdate,
  PaymentTransactionBase,
  PaymentTransactionCreate,
  PaymentTransactionResponse,
  PaymentTransactionList,
  PaymentStats,
  UserBalanceAdjustPayload,
  UserBalanceSummary,
  UserBalanceUsersResponse
} from '../types/payment';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const API_BASE = `${API_BASE_URL}/api/payment`;

const getAccessToken = () => {
  if (typeof globalThis === 'undefined' || !('localStorage' in globalThis)) {
    return null;
  }
  return globalThis.localStorage.getItem('chronos_access_token') || globalThis.localStorage.getItem('access_token');
};

function withAuth(init: RequestInit = {}): RequestInit {
  const token = getAccessToken();
  const headers = new Headers(init.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return {
    ...init,
    headers,
    credentials: 'include',
  };
}

// Helper Functions
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error ${response.status}`);
  }
  return response.json();
}

function buildQueryString(params: Record<string, unknown>): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.append(key, String(value));
    }
  });
  return query.toString() ? `?${query.toString()}` : '';
}

// Payment Methods API
export async function getPaymentMethods(
  provider?: string,
  isActive?: boolean,
  sortBy: string = 'name',
  sortOrder: 'asc' | 'desc' = 'asc',
  page: number = 1,
  pageSize: number = 20
): Promise<PaymentMethodList> {
  const params: Record<string, unknown> = {
    page,
    page_size: pageSize,
    sort_by: sortBy,
    sort_order: sortOrder
  };
  
  if (provider) params.provider = provider;
  if (isActive !== undefined) params.is_active = isActive;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/methods${queryString}`, withAuth());
  return handleResponse<PaymentMethodList>(response);
}

export async function getPaymentMethod(methodId: number): Promise<PaymentMethod> {
  const response = await fetch(`${API_BASE}/methods/${methodId}`, withAuth());
  return handleResponse<PaymentMethod>(response);
}

export async function createPaymentMethod(method: PaymentMethodCreate): Promise<PaymentMethod> {
  const response = await fetch(`${API_BASE}/methods`, withAuth({
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(method),
  }));
  return handleResponse<PaymentMethod>(response);
}

export async function updatePaymentMethod(
  methodId: number,
  method: PaymentMethodUpdate
): Promise<PaymentMethod> {
  const response = await fetch(`${API_BASE}/methods/${methodId}`, withAuth({
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(method),
  }));
  return handleResponse<PaymentMethod>(response);
}

export async function deletePaymentMethod(methodId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/methods/${methodId}`, withAuth({
    method: 'DELETE',
  }));
  if (!response.ok) {
    throw new Error('Failed to delete payment method');
  }
}

// Payment Settings API
export async function getPaymentSettings(): Promise<PaymentSettings> {
  const response = await fetch(`${API_BASE}/settings`, withAuth());
  return handleResponse<PaymentSettings>(response);
}

export async function updatePaymentSettings(
  settings: PaymentSettingsUpdate
): Promise<PaymentSettings> {
  const response = await fetch(`${API_BASE}/settings`, withAuth({
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  }));
  return handleResponse<PaymentSettings>(response);
}

// Payment Transactions API
export async function getPaymentTransactions(
  userId?: number,
  methodId?: number,
  status?: string,
  transactionType?: string,
  sortBy: string = 'created_at',
  sortOrder: 'asc' | 'desc' = 'desc',
  page: number = 1,
  pageSize: number = 20
): Promise<PaymentTransactionList> {
  const params: Record<string, unknown> = {
    page,
    page_size: pageSize,
    sort_by: sortBy,
    sort_order: sortOrder
  };
  
  if (userId) params.user_id = userId;
  if (methodId) params.method_id = methodId;
  if (status) params.status = status;
  if (transactionType) params.transaction_type = transactionType;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/transactions${queryString}`, withAuth());
  return handleResponse<PaymentTransactionList>(response);
}

export async function createPaymentTransaction(
  transaction: PaymentTransactionCreate
): Promise<PaymentTransactionResponse> {
  const response = await fetch(`${API_BASE}/transactions`, withAuth({
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(transaction),
  }));
  return handleResponse<PaymentTransactionResponse>(response);
}

// Payment Statistics API
export async function getPaymentStats(): Promise<PaymentStats> {
  const response = await fetch(`${API_BASE}/stats`, withAuth());
  return handleResponse<PaymentStats>(response);
}

export async function getBalanceUsers(query?: string): Promise<UserBalanceUsersResponse> {
  const qs = query ? `?query=${encodeURIComponent(query)}` : ''
  const response = await fetch(`${API_BASE}/balances/users${qs}`, withAuth())
  return handleResponse<UserBalanceUsersResponse>(response)
}

export async function getUserBalanceSummary(userId: number): Promise<UserBalanceSummary> {
  const response = await fetch(`${API_BASE}/balances/users/${userId}`, withAuth())
  return handleResponse<UserBalanceSummary>(response)
}

export async function adjustUserBalance(userId: number, payload: UserBalanceAdjustPayload): Promise<UserBalanceSummary> {
  const response = await fetch(`${API_BASE}/balances/users/${userId}/adjust`, withAuth({
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }))
  return handleResponse<UserBalanceSummary>(response)
}
