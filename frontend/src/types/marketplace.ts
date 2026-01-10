/**
 * Marketplace Types
 * Type definitions for marketplace functionality in Chronos AI Agent Builder Studio
 */

// ============== Enum Types ==============

export type ListingType = 'AGENT' | 'SUBAGENT';

export type Visibility = 'PUBLIC' | 'PRIVATE' | 'UNLISTED';

export type ModerationStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

// ============== Marketplace Category Types ==============

export interface MarketplaceCategory {
    id: number;
    name: string;
    display_name: string;
    description?: string;
    icon?: string;
    is_active: boolean;
    sort_order: number;
    created_at: string;
    updated_at: string;
}

export interface MarketplaceCategoryCreate {
    name: string;
    display_name: string;
    description?: string;
    icon?: string;
    is_active?: boolean;
    sort_order?: number;
}

export interface MarketplaceCategoryUpdate {
    display_name?: string;
    description?: string;
    icon?: string;
    is_active?: boolean;
    sort_order?: number;
}

export interface MarketplaceCategoryList {
    items: MarketplaceCategory[];
    total: number;
    page: number;
    page_size: number;
}

// ============== Marketplace Tag Types ==============

export interface MarketplaceTag {
    id: number;
    name: string;
    display_name: string;
    description?: string;
    is_active: boolean;
    usage_count: number;
    created_at: string;
    updated_at: string;
}

export interface MarketplaceTagCreate {
    name: string;
    display_name: string;
    description?: string;
    is_active?: boolean;
}

export interface MarketplaceTagUpdate {
    display_name?: string;
    description?: string;
    is_active?: boolean;
}

export interface MarketplaceTagList {
    items: MarketplaceTag[];
    total: number;
    page: number;
    page_size: number;
}

// ============== Marketplace Listing Types ==============

export interface MarketplaceListing {
    id: number;
    agent_id: number;
    author_id: number;
    title: string;
    description?: string;
    category_id?: number;
    tags?: string[];
    listing_type: ListingType;
    visibility: Visibility;
    version?: string;
    preview_images?: string[];
    demo_video_url?: string;
    schema_data?: Record<string, unknown>;
    moderation_status: ModerationStatus;
    moderation_notes?: string;
    install_count: number;
    rating_average: number;
    rating_count: number;
    view_count: number;
    published_at?: string;
    created_at: string;
    updated_at: string;
}

export interface MarketplaceListingCreate {
    agent_id: number;
    title: string;
    description?: string;
    category_id?: number;
    tags?: string[];
    listing_type?: ListingType;
    visibility?: Visibility;
    version?: string;
    preview_images?: string[];
    demo_video_url?: string;
    schema_data?: Record<string, unknown>;
}

export interface MarketplaceListingUpdate {
    title?: string;
    description?: string;
    category_id?: number;
    tags?: string[];
    visibility?: Visibility;
    version?: string;
    preview_images?: string[];
    demo_video_url?: string;
    schema_data?: Record<string, unknown>;
}

export interface MarketplaceListingList {
    items: MarketplaceListing[];
    total: number;
    page: number;
    page_size: number;
    has_more: boolean;
}

// ============== Marketplace Installation Types ==============

export interface MarketplaceInstallation {
    id: number;
    listing_id: number;
    user_id: number;
    agent_id: number;
    installed_at: string;
}

export interface MarketplaceInstallationCreate {
    listing_id: number;
}

export interface MarketplaceInstallationResponse {
    id: number;
    listing_id: number;
    user_id: number;
    agent_id: number;
    installed_at: string;
}

// ============== Marketplace Review Types ==============

export interface MarketplaceReview {
    id: number;
    listing_id: number;
    user_id: number;
    rating: number;
    review_text?: string;
    created_at: string;
    updated_at: string;
}

export interface MarketplaceReviewCreate {
    listing_id: number;
    rating: number;
    review_text?: string;
}

export interface MarketplaceReviewUpdate {
    rating?: number;
    review_text?: string;
}

export interface MarketplaceReviewList {
    items: MarketplaceReview[];
    total: number;
    page: number;
    page_size: number;
}

// ============== Search and Filter Types ==============

export interface MarketplaceSearchParams {
    query?: string;
    category?: string;
    tags?: string[];
    listing_type?: ListingType;
    sort_by?: string; // created_at, rating, installs, views
    sort_order?: string; // asc, desc
    page?: number;
    page_size?: number;
}

// ============== Agent Types ==============

export interface Agent {
    id: number;
    name: string;
    description?: string;
    status: string;
    model_config?: Record<string, unknown>;
    system_prompt?: string;
    user_prompt_template?: string;
    sub_agent_config?: Record<string, unknown>;
    tags?: string[];
    metadata?: Record<string, unknown>;
    usage_count: number;
    success_rate: number;
    avg_response_time: number;
    owner_id: number;
    created_at: string;
    updated_at: string;
    version?: string;
    icon?: string;
    color?: string;
    preview_image?: string;
}

// ============== Copy Statistics Types ==============

export interface CopyStatistics {
    listing_id: number;
    total_installs: number;
    recent_installs: number;
    unique_users: number;
    listing_title: string;
}

// ============== Copied Agents List Types ==============

export interface CopiedAgent {
    agent_id: number;
    name: string;
    description: string;
    status: string;
    created_at: string;
    updated_at: string;
    listing_id: number;
    listing_title: string;
    original_agent_id: number;
    installed_at: string;
    author_id: number;
    is_copy: boolean;
    metadata: Record<string, any>;
}

export interface CopiedAgentsList {
    items: CopiedAgent[];
    total: number;
    page: number;
    page_size: number;
    has_more: boolean;
}

// ============== UI State Types ==============

export interface PublishingFormState {
    agentId: number;
    title: string;
    description: string;
    categoryId?: number;
    selectedTags: string[];
    listingType: ListingType;
    visibility: Visibility;
    version: string;
    previewImages: string[];
    demoVideoUrl?: string;
    pricingModel: 'free' | 'paid';
    price?: number;
    licenseType: string;
    supportInformation: string;
    isSubmitting: boolean;
    errors: Record<string, string>;
}

export interface PublishModalState {
    isOpen: boolean;
    publishToChannels: boolean;
    publishToMarketplace: boolean;
    formState: PublishingFormState;
    availableCategories: MarketplaceCategory[];
    availableTags: MarketplaceTag[];
    isLoadingCategories: boolean;
    isLoadingTags: boolean;
}