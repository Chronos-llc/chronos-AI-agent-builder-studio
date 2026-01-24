/**
 * Support System Types
 * Based on backend/app/schemas/support_system.py
 */

// Support Status Enum
export enum SupportStatus {
  OPEN = "OPEN",
  IN_PROGRESS = "IN_PROGRESS",
  RESOLVED = "RESOLVED",
  CLOSED = "CLOSED",
}

// Support Priority Enum
export enum SupportPriority {
  LOW = "LOW",
  NORMAL = "NORMAL",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

// Support Category Enum
export enum SupportCategory {
  BUG = "BUG",
  FEATURE_REQUEST = "FEATURE_REQUEST",
  BILLING = "BILLING",
  TECHNICAL = "TECHNICAL",
  ACCOUNT = "ACCOUNT",
  OTHER = "OTHER",
}

// Support Message Base Type
export interface SupportMessageBase {
  subject: string;
  message: string;
  priority: SupportPriority;
  category?: SupportCategory;
}

// Support Message Create Type
export type SupportMessageCreate = SupportMessageBase;

// Support Message Update Type
export interface SupportMessageUpdate {
  subject?: string;
  message?: string;
  status?: SupportStatus;
  priority?: SupportPriority;
  assigned_to?: number;
  category?: SupportCategory;
  resolved_at?: string;
}

// Support Message Response Type
export interface SupportMessageResponse extends SupportMessageBase {
  id: number;
  user_id: number;
  status: SupportStatus;
  assigned_to?: number;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  user: {
    id: number;
    name: string;
    email: string;
  };
  replies: SupportMessageReplyResponse[];
}

// Support Message List Type (paginated results)
export interface SupportMessageList {
  items: SupportMessageResponse[];
  total: number;
  page: number;
  page_size: number;
}

// Support Message Reply Base Type
export interface SupportMessageReplyBase {
  reply_text: string;
}

// Support Message Reply Create Type
export type SupportMessageReplyCreate = SupportMessageReplyBase;

// Support Message Reply Response Type
export interface SupportMessageReplyResponse extends SupportMessageReplyBase {
  id: number;
  message_id: number;
  user_id: number;
  is_admin: boolean;
  created_at: string;
  user: {
    id: number;
    name: string;
    email: string;
  };
}

// Support Message Reply List Type (paginated results)
export interface SupportMessageReplyList {
  items: SupportMessageReplyResponse[];
  total: number;
  page: number;
  page_size: number;
}

// Support Search Params Type
export interface SupportSearchParams {
  query?: string;
  status?: SupportStatus;
  priority?: SupportPriority;
  category?: SupportCategory;
  assigned_to?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

// Export all types
export type SupportMessage = SupportMessageResponse;
export type SupportMessageReply = SupportMessageReplyResponse;
