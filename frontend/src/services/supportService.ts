/**
 * Support System API Service
 * Handles all support messaging related API calls
 */

import type {
  SupportMessage,
  SupportMessageCreate,
  SupportMessageUpdate,
  SupportMessageList,
  SupportMessageReply,
  SupportMessageReplyCreate,
  SupportMessageReplyList,
  SupportSearchParams,
  SupportStatus,
  SupportPriority,
  SupportCategory
} from '../types/support';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '';
const API_BASE = `${API_BASE_URL}/api/support`;

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

// Support Messages API
export async function getSupportMessages(
  status?: SupportStatus,
  priority?: SupportPriority,
  category?: SupportCategory,
  assignedTo?: number,
  searchQuery?: string,
  sortBy: string = 'created_at',
  sortOrder: 'asc' | 'desc' = 'desc',
  page: number = 1,
  pageSize: number = 20
): Promise<SupportMessageList> {
  const params: Record<string, unknown> = {
    page,
    page_size: pageSize,
    sort_by: sortBy,
    sort_order: sortOrder
  };
  
  if (status) params.status = status;
  if (priority) params.priority = priority;
  if (category) params.category = category;
  if (assignedTo) params.assigned_to = assignedTo;
  if (searchQuery) params.search_query = searchQuery;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/messages${queryString}`);
  return handleResponse<SupportMessageList>(response);
}

export async function getSupportMessage(messageId: number): Promise<SupportMessage> {
  const response = await fetch(`${API_BASE}/messages/${messageId}`);
  return handleResponse<SupportMessage>(response);
}

export async function createSupportMessage(message: SupportMessageCreate): Promise<SupportMessage> {
  const response = await fetch(`${API_BASE}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message),
  });
  return handleResponse<SupportMessage>(response);
}

export async function updateSupportMessage(
  messageId: number,
  message: SupportMessageUpdate
): Promise<SupportMessage> {
  const response = await fetch(`${API_BASE}/messages/${messageId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(message),
  });
  return handleResponse<SupportMessage>(response);
}

export async function createSupportReply(
  messageId: number,
  reply: SupportMessageReplyCreate
): Promise<SupportMessageReply> {
  const response = await fetch(`${API_BASE}/messages/${messageId}/replies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reply),
  });
  return handleResponse<SupportMessageReply>(response);
}

export async function getSupportReplies(messageId: number): Promise<SupportMessageReplyList> {
  const response = await fetch(`${API_BASE}/messages/${messageId}/replies`);
  return handleResponse<SupportMessageReplyList>(response);
}

export async function searchSupportMessages(params: SupportSearchParams): Promise<SupportMessageList> {
  const response = await fetch(`${API_BASE}/messages/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return handleResponse<SupportMessageList>(response);
}

export async function getMySupportStats(): Promise<{
  open: number;
  in_progress: number;
  resolved: number;
  closed: number;
  total: number;
}> {
  const response = await fetch(`${API_BASE}/my-messages/stats`);
  return handleResponse<{ open: number; in_progress: number; resolved: number; closed: number; total: number }>(response);
}

export async function deleteSupportMessage(messageId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/messages/${messageId}`, {
    method: 'DELETE'
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error ${response.status}`);
  }
}

export async function getAdminSupportStats(): Promise<{
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_category: Record<string, number>;
}> {
  const response = await fetch(`${API_BASE}/admin/stats`);
  return handleResponse<{
    by_status: Record<string, number>;
    by_priority: Record<string, number>;
    by_category: Record<string, number>;
  }>(response);
}
