/**
 * Platform Updates API Service
 * Handles all platform updates related API calls
 */

import type {
  PlatformUpdate,
  PlatformUpdateCreate,
  PlatformUpdateUpdate,
  PlatformUpdateList,
  UserUpdateViewList,
  UpdateType,
  UpdatePriority,
  TargetAudience
} from '../types/platformUpdates';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/updates`;

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

// Platform Updates API
export async function getPlatformUpdates(
  updateType?: UpdateType,
  priority?: UpdatePriority,
  targetAudience?: TargetAudience,
  isPublished?: boolean,
  searchQuery?: string,
  sortBy: string = 'published_at',
  sortOrder: 'asc' | 'desc' = 'desc',
  page: number = 1,
  pageSize: number = 20
): Promise<PlatformUpdateList> {
  const params: Record<string, unknown> = {
    page,
    page_size: pageSize,
    sort_by: sortBy,
    sort_order: sortOrder
  };
  
  if (updateType) params.update_type = updateType;
  if (priority) params.priority = priority;
  if (targetAudience) params.target_audience = targetAudience;
  if (isPublished !== undefined) params.is_published = isPublished;
  if (searchQuery) params.search_query = searchQuery;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}${queryString}`);
  return handleResponse<PlatformUpdateList>(response);
}

export async function getPlatformUpdate(updateId: number): Promise<PlatformUpdate> {
  const response = await fetch(`${API_BASE}/${updateId}`);
  return handleResponse<PlatformUpdate>(response);
}

export async function createPlatformUpdate(update: PlatformUpdateCreate): Promise<PlatformUpdate> {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(update),
  });
  return handleResponse<PlatformUpdate>(response);
}

export async function updatePlatformUpdate(
  updateId: number,
  update: PlatformUpdateUpdate
): Promise<PlatformUpdate> {
  const response = await fetch(`${API_BASE}/${updateId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(update),
  });
  return handleResponse<PlatformUpdate>(response);
}

export async function deletePlatformUpdate(updateId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/${updateId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete platform update');
  }
}

export async function getUpdateViews(updateId: number): Promise<UserUpdateViewList> {
  const response = await fetch(`${API_BASE}/${updateId}/views`);
  return handleResponse<UserUpdateViewList>(response);
}

export async function getUnviewedUpdates(): Promise<PlatformUpdateList> {
  const response = await fetch('/api/my-updates/unviewed');
  return handleResponse<PlatformUpdateList>(response);
}

export async function markUpdateViewed(updateId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/${updateId}/mark-viewed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    throw new Error('Failed to mark update as viewed');
  }
}