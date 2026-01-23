/**
 * Platform Updates Types
 * Based on backend/app/schemas/platform_updates.py
 */

// Update Type Enum
export enum UpdateType {
  FEATURE = "FEATURE",
  BUG_FIX = "BUG_FIX",
  ANNOUNCEMENT = "ANNOUNCEMENT",
  MAINTENANCE = "MAINTENANCE",
  SECURITY = "SECURITY",
}

// Update Priority Enum
export enum UpdatePriority {
  LOW = "LOW",
  NORMAL = "NORMAL",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

// Target Audience Enum
export enum TargetAudience {
  ALL = "ALL",
  ADMIN = "ADMIN",
  USER = "USER",
}

// Platform Update Base Type
export interface PlatformUpdateBase {
  title: string;
  description: string;
  update_type: UpdateType;
  priority: UpdatePriority;
  media_type?: string;
  media_urls?: string[];
  thumbnail_url?: string;
  target_audience: TargetAudience;
}

// Platform Update Create Type
export type PlatformUpdateCreate = PlatformUpdateBase;

// Platform Update Update Type
export interface PlatformUpdateUpdate {
  title?: string;
  description?: string;
  update_type?: UpdateType;
  priority?: UpdatePriority;
  media_type?: string;
  media_urls?: string[];
  thumbnail_url?: string;
  target_audience?: TargetAudience;
  is_published?: boolean;
  published_at?: string | null;
  expires_at?: string | null;
}

// Platform Update Response Type
export interface PlatformUpdateResponse extends PlatformUpdateBase {
  id: number;
  is_published: boolean;
  view_count: number;
  published_at?: string | null;
  expires_at?: string | null;
  created_at: string;
  updated_at: string;
}

// Platform Update List Type (paginated results)
export interface PlatformUpdateList {
  items: PlatformUpdateResponse[];
  total: number;
  page: number;
  page_size: number;
}

// User Update View Response Type
export interface UserUpdateViewResponse {
  id: number;
  update_id: number;
  user_id: number;
  viewed_at: string;
}

// User Update View List Type (paginated results)
export interface UserUpdateViewList {
  items: UserUpdateViewResponse[];
  total: number;
  page: number;
  page_size: number;
}

// Export all types
export type PlatformUpdate = PlatformUpdateResponse;
