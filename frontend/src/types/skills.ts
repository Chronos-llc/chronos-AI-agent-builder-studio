/**
 * Skills Types
 * Type definitions for skills functionality in Chronos AI Agent Builder Studio
 */

// ============== Skill Types ==============

export interface Skill {
    id: number;
    name: string;
    display_name: string;
    description?: string;
    category?: string;
    icon?: string;
    version?: string;
    parameters?: Record<string, any>;
    tags?: string[];
    file_path: string;
    file_size?: number;
    content_preview?: string;
    is_active: boolean;
    is_premium: boolean;
    install_count: number;
    download_count?: number;
    submission_status?: string;
    visibility?: string;
    scan_status?: string;
    scan_confidence?: number;
    scan_summary?: string;
    created_by?: number;
    created_at: string;
    updated_at: string;
}

export interface SkillCreate {
    name: string;
    display_name: string;
    description?: string;
    category?: string;
    icon?: string;
    version?: string;
    parameters?: Record<string, any>;
    tags?: string[];
    file_path: string;
    content_preview?: string;
    is_active?: boolean;
    is_premium?: boolean;
}

export interface SkillUpdate {
    display_name?: string;
    description?: string;
    category?: string;
    icon?: string;
    version?: string;
    parameters?: Record<string, any>;
    tags?: string[];
    file_path?: string;
    content_preview?: string;
    is_active?: boolean;
    is_premium?: boolean;
}

export interface SkillList {
    items: Skill[];
    total: number;
    page: number;
    page_size: number;
    has_more: boolean;
}

// ============== Agent Skill Installation Types ==============

export interface AgentSkillInstallation {
    id: number;
    agent_id: number;
    skill_id: number;
    knowledge_file_id?: number;
    configuration?: Record<string, any>;
    is_enabled: boolean;
    installed_at: string;
    created_at: string;
    updated_at: string;
    skill?: Skill;
}

export interface AgentSkillInstallationCreate {
    skill_id: number;
    configuration?: Record<string, any>;
}

export interface AgentSkillInstallationUpdate {
    configuration?: Record<string, any>;
    is_enabled?: boolean;
}

export interface AgentSkillInstallationList {
    items: AgentSkillInstallation[];
    total: number;
}

// ============== Skill Execution Types ==============

export interface SkillExecutionRequest {
    skill_id: number;
    parameters?: Record<string, any>;
    context?: Record<string, any>;
}

export interface SkillExecutionResponse {
    success: boolean;
    result?: any;
    error?: string;
    execution_time?: number;
}

// ============== Skill Statistics Types ==============

export interface SkillStatistics {
    total_skills: number;
    active_skills: number;
    total_installations: number;
    popular_categories: { category: string; count: number }[];
    recent_skills: Skill[];
}

// ============== Search and Filter Types ==============

export interface SkillSearchParams {
    query?: string;
    category?: string;
    tags?: string[];
    is_active?: boolean;
    is_premium?: boolean;
    sort_by?: string; // created_at, install_count, name
    sort_order?: string; // asc, desc
    page?: number;
    page_size?: number;
}

// ============== UI State Types ==============

export interface SkillCreatorState {
    name: string;
    display_name: string;
    description: string;
    category: string;
    icon: string;
    version: string;
    parameters: Record<string, any>;
    tags: string[];
    file_path: string;
    content_preview: string;
    is_active: boolean;
    is_premium: boolean;
    isSubmitting: boolean;
    errors: Record<string, string>;
}

export interface SkillSelectorState {
    selectedCategory?: string;
    searchQuery: string;
    selectedTags: string[];
    showPremiumOnly: boolean;
    currentPage: number;
    pageSize: number;
    isLoading: boolean;
    skills: Skill[];
    totalSkills: number;
}

export interface SkillsConfigurationState {
    agentId: number;
    installedSkills: AgentSkillInstallation[];
    availableSkills: Skill[];
    isLoading: boolean;
    searchQuery: string;
    selectedCategory?: string;
    showPremiumOnly: boolean;
}

// ============== Skill Parameter Types ==============

export interface SkillParameter {
    name: string;
    type: 'string' | 'number' | 'boolean' | 'object' | 'array';
    description: string;
    required?: boolean;
    default?: any;
    enum?: string[];
    minimum?: number;
    maximum?: number;
    minLength?: number;
    maxLength?: number;
}

export interface SkillParameterGroup {
    group_name: string;
    parameters: SkillParameter[];
    description?: string;
}
