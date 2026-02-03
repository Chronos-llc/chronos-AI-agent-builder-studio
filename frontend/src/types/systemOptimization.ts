// System Optimization Types
// TypeScript interfaces matching backend schemas for system optimization and performance tuning

// Enums (exported as string literal types for TypeScript)
export type MetricType =
    | 'CPU'
    | 'MEMORY'
    | 'DISK'
    | 'NETWORK'
    | 'RESPONSE_TIME'
    | 'THROUGHPUT';

export type AlertCondition = 'GT' | 'LT' | 'EQ' | 'GTE' | 'LTE';

export type AlertSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type RecommendationType = 'PERFORMANCE' | 'COST' | 'RELIABILITY' | 'SCALABILITY';

export type EffortLevel = 'LOW' | 'MEDIUM' | 'HIGH';

export type RecommendationStatus = 'PENDING' | 'APPLIED' | 'DISMISSED' | 'EXPIRED';

export type AggregationType = 'avg' | 'sum' | 'max' | 'min';

export type SystemHealthStatus = 'healthy' | 'degraded' | 'unhealthy';

// ==================== System Metrics ====================

export interface SystemMetrics {
    id: number;
    metric_type: MetricType;
    metric_name: string;
    metric_value: number;
    unit?: string;
    tags?: Record<string, unknown>;
    timestamp: string;
    created_at: string;
}

export interface SystemMetricsCreate {
    metric_type: MetricType;
    metric_name: string;
    metric_value: number;
    unit?: string;
    tags?: Record<string, unknown>;
    timestamp?: string;
}

// ==================== Agent Performance Metrics ====================

export interface AgentPerformanceMetrics {
    id: number;
    agent_id: number;
    execution_time_ms?: number;
    token_count?: number;
    cost?: number;
    success_rate?: number;
    avg_response_time?: number;
    error_count: number;
    timestamp: string;
    created_at: string;
}

export interface AgentPerformanceMetricsCreate {
    agent_id: number;
    execution_time_ms?: number;
    token_count?: number;
    cost?: number;
    success_rate?: number;
    avg_response_time?: number;
    error_count?: number;
    timestamp?: string;
}

export interface AgentPerformanceAggregatedStats {
    agent_id: number;
    total_executions: number;
    avg_execution_time_ms?: number;
    max_execution_time_ms?: number;
    min_execution_time_ms?: number;
    total_tokens?: number;
    total_cost?: number;
    avg_success_rate?: number;
    total_errors: number;
    avg_response_time_ms?: number;
}

// ==================== Optimization Recommendations ====================

export interface OptimizationRecommendation {
    id: number;
    agent_id?: number;
    recommendation_type: RecommendationType;
    title: string;
    description: string;
    current_value?: string;
    recommended_value?: string;
    impact_score: number;
    effort_level: EffortLevel;
    status: RecommendationStatus;
    created_at: string;
    expires_at?: string;
}

export interface OptimizationRecommendationCreate {
    agent_id?: number;
    recommendation_type: RecommendationType;
    title: string;
    description: string;
    current_value?: string;
    recommended_value?: string;
    impact_score: number;
    effort_level: EffortLevel;
    expires_at?: string;
}

export interface RecommendationApplyRequest {
    apply_changes?: boolean;
    auto_approve?: boolean;
    notes?: string;
}

// ==================== Performance Baselines ====================

export interface PerformanceBaseline {
    id: number;
    agent_id?: number;
    metric_type: MetricType;
    baseline_value: number;
    threshold_value?: number;
    measurement_window: number;
    created_at: string;
    updated_at: string;
}

export interface PerformanceBaselineCreate {
    agent_id?: number;
    metric_type: MetricType;
    baseline_value: number;
    threshold_value?: number;
    measurement_window?: number;
}

export interface PerformanceBaselineUpdate {
    baseline_value?: number;
    threshold_value?: number;
    measurement_window?: number;
}

// ==================== Alert Rules ====================

export interface AlertRule {
    id: number;
    name: string;
    description?: string;
    metric_type: MetricType;
    condition: AlertCondition;
    threshold_value: number;
    severity: AlertSeverity;
    is_active: boolean;
    cooldown_period: number;
    created_at: string;
}

export interface AlertRuleCreate {
    name: string;
    description?: string;
    metric_type: MetricType;
    condition: AlertCondition;
    threshold_value: number;
    severity: AlertSeverity;
    is_active?: boolean;
    cooldown_period?: number;
}

export interface AlertRuleUpdate {
    name?: string;
    description?: string;
    metric_type?: MetricType;
    condition?: AlertCondition;
    threshold_value?: number;
    severity?: AlertSeverity;
    is_active?: boolean;
    cooldown_period?: number;
}

export interface AlertHistory {
    id: number;
    alert_rule_id: number;
    triggered_value: number;
    triggered_at: string;
    acknowledged: boolean;
    acknowledged_at?: string;
    acknowledged_by?: string;
    notes?: string;
}

export interface ActiveAlert {
    alert_rule_id: number;
    alert_rule_name: string;
    triggered_value: number;
    triggered_at: string;
    severity: AlertSeverity;
    condition: string;
}

// ==================== Metrics Query ====================

export interface MetricsQueryRequest {
    metric_types?: MetricType[];
    metric_names?: string[];
    start_time: string;
    end_time: string;
    aggregation: AggregationType;
    tags?: Record<string, unknown>;
    limit?: number;
}

export interface MetricsQueryResponse {
    metric_type: MetricType;
    metric_name: string;
    aggregation: string;
    start_time: string;
    end_time: string;
    data_points: Array<{ timestamp: string; value: number }>;
    statistics?: {
        avg: number;
        sum: number;
        max: number;
        min: number;
        count: number;
    };
}

// ==================== System Health ====================

export interface SystemHealthResponse {
    status: SystemHealthStatus;
    metrics: Record<string, {
        latest: number;
        avg: number;
        max: number;
    }>;
    last_updated: string;
    active_alerts: number;
    pending_recommendations: number;
}

// ==================== Dashboard Summary ====================

export interface DashboardSummary {
    system_health: SystemHealthResponse;
    recent_metrics: Array<{
        id: number;
        metric_type: MetricType;
        metric_name: string;
        metric_value: number;
        timestamp: string;
        unit?: string;
    }>;
    top_recommendations: Array<{
        id: number;
        title: string;
        recommendation_type: RecommendationType;
        impact_score: number;
        effort_level: EffortLevel;
        status: RecommendationStatus;
        description: string;
        created_at: string;
    }>;
    active_alerts: ActiveAlert[];
    generated_at: string;
}

// ==================== Chart Data Types ====================

export interface TimeSeriesDataPoint {
    timestamp: string;
    value: number;
}

export interface TimeSeriesChartData {
    metric_type: MetricType;
    metric_name: string;
    data: TimeSeriesDataPoint[];
    color?: string;
}

export interface MultiSeriesChartData {
    title: string;
    series: Array<{
        name: string;
        data: TimeSeriesDataPoint[];
        color?: string;
    }>;
}

export interface BarChartData {
    label: string;
    value: number;
    color?: string;
}

export interface HeatMapData {
    x: string;
    y: string;
    value: number;
}

// ==================== Filter Types ====================

export interface MetricsFilter {
    metric_types?: MetricType[];
    start_time?: string;
    end_time?: string;
    aggregation?: AggregationType;
}

export interface RecommendationsFilter {
    agent_id?: number;
    recommendation_type?: RecommendationType;
    status?: RecommendationStatus;
    impact_score_min?: number;
}

export interface AlertsFilter {
    metric_type?: MetricType;
    severity?: AlertSeverity;
    is_active?: boolean;
}

export interface DateRange {
    start: Date;
    end: Date;
}

// ==================== API Response Types ====================

export interface ApiResponse<T> {
    data: T;
    success: boolean;
    message?: string;
    error?: string;
}

export interface PaginatedResponse<T> {
    data: T[];
    total: number;
    page: number;
    limit: number;
    has_more: boolean;
}