/**
 * FUZZY Meta-Agent TypeScript Types
 * Types for managing FUZZY configuration, monitoring, and testing
 */

// ============== Enums ==============

export type FuzzyActionType =
    | 'create_agent'
    | 'update_agent'
    | 'delete_agent'
    | 'add_tool'
    | 'remove_tool'
    | 'update_instructions'
    | 'add_knowledge'
    | 'configure_channel'
    | 'publish_agent'
    | 'unpublish_agent'
    | 'query_agents'
    | 'query_tools'
    | 'query_integrations'

export type FuzzyActionStatus =
    | 'pending'
    | 'executing'
    | 'completed'
    | 'failed'
    | 'rolled_back'

export type FuzzyToolStatus = 'enabled' | 'disabled' | 'maintenance'

// ============== Configuration Types ==============

export interface FuzzyConfiguration {
    id?: number
    system_instructions: string
    personality: string
    temperature: number
    max_tokens: number
    model: string
    provider: string
    rate_limit_hourly: number
    rate_limit_daily: number
    enabled_tools: string[]
    permissions: string[]
    auto_approve_actions: boolean
    require_confirmation: boolean
    logging_level: 'debug' | 'info' | 'warning' | 'error'
    created_at?: string
    updated_at?: string
}

export interface FuzzyConfigurationUpdate {
    system_instructions?: string
    personality?: string
    temperature?: number
    max_tokens?: number
    model?: string
    provider?: string
    rate_limit_hourly?: number
    rate_limit_daily?: number
    enabled_tools?: string[]
    permissions?: string[]
    auto_approve_actions?: boolean
    require_confirmation?: boolean
    logging_level?: 'debug' | 'info' | 'warning' | 'error'
}

// ============== Tool Management Types ==============

export interface FuzzyTool {
    id: string
    name: string
    description: string
    category: string
    status: FuzzyToolStatus
    usage_count: number
    success_rate: number
    average_execution_time: number
    last_used?: string
    parameters?: Record<string, any>
    enabled: boolean
}

export interface FuzzyToolConfig {
    tool_id: string
    enabled: boolean
    parameters?: Record<string, any>
    rate_limit?: number
    timeout?: number
}

// ============== Session Types ==============

export interface FuzzySession {
    id: number
    user_id: number
    session_token: string
    is_active: boolean
    context?: Record<string, any>
    started_at: string
    last_activity_at: string
    ended_at?: string
}

export interface FuzzySessionCreate {
    context?: Record<string, any>
}

// ============== Action Audit Types ==============

export interface FuzzyAction {
    id: number
    session_id: number
    user_id: number
    action_type: FuzzyActionType
    action_name: string
    description?: string
    parameters?: Record<string, any>
    result?: Record<string, any>
    error_message?: string
    status: FuzzyActionStatus
    execution_time_ms?: number
    affected_resource_type?: string
    affected_resource_id?: number
    can_rollback: boolean
    created_at: string
}

export interface FuzzyActionList {
    actions: FuzzyAction[]
    total: number
    limit: number
    offset: number
}

// ============== Monitoring Types ==============

export interface FuzzyUsageStatistics {
    total_sessions: number
    active_sessions: number
    total_actions: number
    successful_actions: number
    failed_actions: number
    average_response_time: number
    actions_per_hour: number
    actions_per_day: number
    unique_users: number
    most_used_tools: Array<{
        tool_name: string
        usage_count: number
    }>
}

export interface FuzzyPerformanceMetrics {
    uptime_percentage: number
    average_response_time: number
    p95_response_time: number
    p99_response_time: number
    error_rate: number
    success_rate: number
    total_requests: number
    requests_per_minute: number
}

export interface FuzzyHealthStatus {
    status: 'healthy' | 'degraded' | 'down'
    last_check: string
    issues: string[]
    uptime: number
}

// ============== Testing Types ==============

export interface FuzzyTestRequest {
    message: string
    context?: Record<string, any>
    session_id?: number
}

export interface FuzzyTestResponse {
    response: string
    actions_taken: FuzzyAction[]
    execution_time_ms: number
    tokens_used: number
    success: boolean
    error?: string
}

export interface FuzzyConversation {
    id: number
    session_id: number
    messages: FuzzyMessage[]
    created_at: string
}

export interface FuzzyMessage {
    id: number
    role: 'user' | 'assistant' | 'system'
    content: string
    timestamp: string
    actions?: FuzzyAction[]
}

// ============== Rate Limit Types ==============

export interface FuzzyRateLimitStatus {
    user_id: number
    actions_count_hourly: number
    hourly_limit: number
    actions_count_daily: number
    daily_limit: number
    hourly_remaining: number
    daily_remaining: number
    hourly_reset_at: string
    daily_reset_at: string
}

// ============== Export/Import Types ==============

export interface FuzzyConfigurationExport {
    version: string
    exported_at: string
    configuration: FuzzyConfiguration
    enabled_tools: FuzzyToolConfig[]
    metadata?: Record<string, any>
}

export interface FuzzyConfigurationImport {
    configuration: FuzzyConfigurationUpdate
    enabled_tools?: FuzzyToolConfig[]
    overwrite_existing?: boolean
}

// ============== API Response Types ==============

export interface FuzzyApiResponse<T = any> {
    success: boolean
    message: string
    data?: T
    error?: string
}

export interface FuzzyToolResponse {
    success: boolean
    message: string
    data?: Record<string, any>
    action_id?: number
    execution_time_ms?: number
}

// ============== Dashboard Types ==============

export interface FuzzyDashboardData {
    configuration: FuzzyConfiguration
    statistics: FuzzyUsageStatistics
    performance: FuzzyPerformanceMetrics
    health: FuzzyHealthStatus
    recent_actions: FuzzyAction[]
    active_sessions: FuzzySession[]
}

export interface FuzzyActivityLog {
    id: number
    timestamp: string
    level: 'info' | 'warning' | 'error' | 'debug'
    message: string
    details?: Record<string, any>
    user_id?: number
    session_id?: number
}
