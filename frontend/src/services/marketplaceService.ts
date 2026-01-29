/**
 * Marketplace API Service
 * Handles all marketplace-related API calls for Chronos AI Agent Builder Studio
 */

import type {
  MarketplaceCategory,
  MarketplaceTag,
  MarketplaceListing,
  MarketplaceListingCreate,
  MarketplaceListingUpdate,
  MarketplaceInstallation,
  MarketplaceReview,
  MarketplaceSearchParams,
  MarketplaceCategoryList,
  MarketplaceTagList,
  MarketplaceListingList,
  MarketplaceReviewList,
  MarketplaceInstallationResponse
} from '../types/marketplace';

const API_BASE = '/api/marketplace';

// ============== Helper Functions ==============

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
      if (Array.isArray(value)) {
        value.forEach(item => query.append(key, String(item)));
      } else {
        query.append(key, String(value));
      }
    }
  });
  return query.toString() ? `?${query.toString()}` : '';
}

// ============== Category API ==============

export async function getCategories(
  isActive?: boolean,
  page: number = 1,
  pageSize: number = 50
): Promise<MarketplaceCategoryList> {
  const params: Record<string, unknown> = { page, page_size: pageSize };
  if (isActive !== undefined) params.is_active = isActive;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/categories${queryString}`);
  return handleResponse<MarketplaceCategoryList>(response);
}

export async function createCategory(category: Omit<MarketplaceCategory, 'id' | 'created_at' | 'updated_at'>): Promise<MarketplaceCategory> {
  const response = await fetch(`${API_BASE}/categories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(category),
  });
  return handleResponse<MarketplaceCategory>(response);
}

// ============== Tag API ==============

export async function getTags(
  isActive?: boolean,
  minUsage?: number,
  page: number = 1,
  pageSize: number = 50
): Promise<MarketplaceTagList> {
  const params: Record<string, unknown> = { page, page_size: pageSize };
  if (isActive !== undefined) params.is_active = isActive;
  if (minUsage !== undefined) params.min_usage = minUsage;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/tags${queryString}`);
  return handleResponse<MarketplaceTagList>(response);
}

export async function createTag(tag: Omit<MarketplaceTag, 'id' | 'usage_count' | 'created_at' | 'updated_at'>): Promise<MarketplaceTag> {
  const response = await fetch(`${API_BASE}/tags`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tag),
  });
  return handleResponse<MarketplaceTag>(response);
}

// ============== Listing API ==============

export async function getListings(
  category?: string,
  tags?: string[],
  listingType?: string,
  visibility?: string,
  moderationStatus?: string,
  minRating?: number,
  searchQuery?: string,
  sortBy: string = 'created_at',
  sortOrder: string = 'desc',
  page: number = 1,
  pageSize: number = 20
): Promise<MarketplaceListingList> {
  const params: Record<string, unknown> = {
    page,
    page_size: pageSize,
    sort_by: sortBy,
    sort_order: sortOrder
  };
  
  if (category) params.category = category;
  if (tags) params.tags = tags;
  if (listingType) params.listing_type = listingType;
  if (visibility) params.visibility = visibility;
  if (moderationStatus) params.moderation_status = moderationStatus;
  if (minRating) params.min_rating = minRating;
  if (searchQuery) params.search_query = searchQuery;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/listings${queryString}`);
  return handleResponse<MarketplaceListingList>(response);
}

export async function getListing(listingId: number): Promise<MarketplaceListing> {
  const response = await fetch(`${API_BASE}/listings/${listingId}`);
  return handleResponse<MarketplaceListing>(response);
}

export async function createListing(listing: MarketplaceListingCreate): Promise<MarketplaceListing> {
  const response = await fetch(`${API_BASE}/listings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(listing),
  });
  return handleResponse<MarketplaceListing>(response);
}

export async function updateListing(
  listingId: number,
  listing: MarketplaceListingUpdate
): Promise<MarketplaceListing> {
  const response = await fetch(`${API_BASE}/listings/${listingId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(listing),
  });
  return handleResponse<MarketplaceListing>(response);
}

export async function deleteListing(listingId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/listings/${listingId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete listing');
  }
}

// ============== Installation API ==============

export async function installAgent(listingId: number): Promise<MarketplaceInstallationResponse> {
  const response = await fetch(`${API_BASE}/listings/${listingId}/install`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ listing_id: listingId }),
  });
  return handleResponse<MarketplaceInstallationResponse>(response);
}

// ============== Review API ==============

export async function createReview(
  listingId: number,
  review: { rating: number; review_text?: string }
): Promise<MarketplaceReview> {
  const response = await fetch(`${API_BASE}/listings/${listingId}/reviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...review, listing_id: listingId }),
  });
  return handleResponse<MarketplaceReview>(response);
}

export async function getReviews(
  listingId: number,
  minRating?: number,
  page: number = 1,
  pageSize: number = 20
): Promise<MarketplaceReviewList> {
  const params: Record<string, unknown> = { page, page_size: pageSize };
  if (minRating) params.min_rating = minRating;
  
  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/listings/${listingId}/reviews${queryString}`);
  return handleResponse<MarketplaceReviewList>(response);
}

// ============== Search API ==============

export async function searchMarketplace(params: MarketplaceSearchParams): Promise<MarketplaceListingList> {
  const response = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return handleResponse<MarketplaceListingList>(response);
}

// ============== File Upload Helper ==============

export async function uploadFile(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'File upload failed' }));
    throw new Error(error.detail || 'File upload failed');
  }
  
  const result = await response.json();
  return result.url; // Return the URL of the uploaded file
}