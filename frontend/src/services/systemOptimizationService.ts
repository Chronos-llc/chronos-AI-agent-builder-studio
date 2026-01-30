/**
 * System Optimization API Service
 * Performance monitoring, optimization recommendations, and automated tuning
 */

import type {
  SystemMetrics,
  SystemMetricsCreate,
  AgentPerformanceMetrics,
  AgentPerformanceMetricsCreate,
  AgentPerformanceAggregatedStats,
  OptimizationRecommendation,
  OptimizationRecommendationCreate,
  RecommendationApplyRequest,
  PerformanceBaseline,
  PerformanceBaselineCreate,
  PerformanceBaselineUpdate,
  AlertRule,
  AlertRuleCreate,
  AlertRuleUpdate,
  AlertHistory,
  ActiveAlert,
  MetricsQueryRequest,
  MetricsQueryResponse,
  SystemHealthResponse,
  DashboardSummary,
  MetricType,
  RecommendationType,
  AlertSeverity,
  RecommendationStatus,
  AggregationType,
} from '../types/systemOptimization';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/system-optimization`;

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
    if (value !== undefined && value !== null && value !== '') {
      query.append(key, String(value));
    }
  });
  return query.toString() ? `?${query.toString()}` : '';
}

// ============== System Metrics API ==============

export async function getMetrics(
  metricType?: MetricType,
  metricName?: string,
  startTime?: string,
  endTime?: string,
  aggregation: AggregationType = 'avg',
  limit = 1000
): Promise<SystemMetrics[]> {
  const params: Record<string, unknown> = { aggregation, limit };
  if (metricType) params.metric_type = metricType;
  if (metricName) params.metric_name = metricName;
  if (startTime) params.start_time = startTime;
  if (endTime) params.end_time = endTime;

  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/metrics${queryString}`);
  return handleResponse<SystemMetrics[]>(response);
}

export async function queryMetrics(queryRequest: MetricsQueryRequest): Promise<MetricsQueryResponse[]> {
  const response = await fetch(`${API_BASE}/metrics/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(queryRequest),
  });
  return handleResponse<MetricsQueryResponse[]>(response);
}

export async function createMetric(metricData: SystemMetricsCreate): Promise<SystemMetrics> {
  const response = await fetch(`${API_BASE}/metrics`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(metricData),
  });
  return handleResponse<SystemMetrics>(response);
}

// ============== Agent Performance API ==============

export async function getAgentPerformance(
  agentId: number,
  startTime?: string,
  endTime?: string
): Promise<AgentPerformanceAggregatedStats> {
  const params: Record<string, unknown> = {};
  if (startTime) params.start_time = startTime;
  if (endTime) params.end_time = endTime;

  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/agents/${agentId}/performance${queryString}`);
  return handleResponse<AgentPerformanceAggregatedStats>(response);
}

export async function recordAgentPerformance(
  agentId: number,
  performanceData: AgentPerformanceMetricsCreate
): Promise<AgentPerformanceMetrics> {
  const response = await fetch(`${API_BASE}/agents/${agentId}/performance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(performanceData),
  });
  return handleResponse<AgentPerformanceMetrics>(response);
}

// ============== Optimization Recommendations API ==============

export async function listRecommendations(
  agentId?: number,
  recommendationType?: RecommendationType,
  status?: RecommendationStatus,
  impactScoreMin?: number,
  limit = 50
): Promise<OptimizationRecommendation[]> {
  const params: Record<string, unknown> = { limit };
  if (agentId) params.agent_id = agentId;
  if (recommendationType) params.recommendation_type = recommendationType;
  if (status) params.status = status;
  if (impactScoreMin !== undefined) params.impact_score_min = impactScoreMin;

  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/recommendations${queryString}`);
  return handleResponse<OptimizationRecommendation[]>(response);
}

export async function createRecommendation(
  recommendationData: OptimizationRecommendationCreate
): Promise<OptimizationRecommendation> {
  const response = await fetch(`${API_BASE}/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(recommendationData),
  });
  return handleResponse<OptimizationRecommendation>(response);
}

export async function applyRecommendation(
  recommendationId: number,
  applyRequest: RecommendationApplyRequest
): Promise<OptimizationRecommendation> {
  const response = await fetch(`${API_BASE}/recommendations/${recommendationId}/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(applyRequest),
  });
  return handleResponse<OptimizationRecommendation>(response);
}

export async function updateRecommendationStatus(
  recommendationId: number,
  status: RecommendationStatus
): Promise<void> {
  const response = await fetch(`${API_BASE}/recommendations/${recommendationId}/status?status=${status}`, {
    method: 'PUT',
  });
  if (!response.ok) {
    throw new Error('Failed to update recommendation status');
  }
}

export async function generateRecommendations(agentId: number): Promise<{
  agent_id: number;
  recommendations_count: number;
  recommendations: Array<{
    type: RecommendationType;
    title: string;
    description: string;
    impact_score: number;
    effort_level: string;
  }>;
}> {
  const response = await fetch(`${API_BASE}/recommendations/generate/${agentId}`);
  return handleResponse(response);
}

// ============== Performance Baselines API ==============

export async function listBaselines(
  agentId?: number,
  metricType?: MetricType
): Promise<PerformanceBaseline[]> {
  const params: Record<string, unknown> = {};
  if (agentId) params.agent_id = agentId;
  if (metricType) params.metric_type = metricType;

  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/baselines${queryString}`);
  return handleResponse<PerformanceBaseline[]>(response);
}

export async function createBaseline(baseline: PerformanceBaselineCreate): Promise<PerformanceBaseline> {
  const response = await fetch(`${API_BASE}/baselines`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(baseline),
  });
  return handleResponse<PerformanceBaseline>(response);
}

export async function updateBaseline(
  baselineId: number,
  baselineUpdate: PerformanceBaselineUpdate
): Promise<PerformanceBaseline> {
  const response = await fetch(`${API_BASE}/baselines/${baselineId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(baselineUpdate),
  });
  return handleResponse<PerformanceBaseline>(response);
}

export async function deleteBaseline(baselineId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/baselines/${baselineId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete baseline');
  }
}

export async function calculateBaseline(
  agentId: number,
  metricType: MetricType,
  windowSeconds = 3600
): Promise<{
  agent_id: number;
  metric_type: MetricType;
  window_seconds: number;
  baseline_value: number | null;
}> {
  const queryString = buildQueryString({ window: windowSeconds });
  const response = await fetch(`${API_BASE}/baselines/calculate/${agentId}?metric_type=${metricType}${queryString}`);
  return handleResponse(response);
}

// ============== Alert Rules API ==============

export async function listAlerts(
  metricType?: MetricType,
  severity?: AlertSeverity,
  isActive?: boolean
): Promise<AlertRule[]> {
  const params: Record<string, unknown> = {};
  if (metricType) params.metric_type = metricType;
  if (severity) params.severity = severity;
  if (isActive !== undefined) params.is_active = isActive;

  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/alerts${queryString}`);
  return handleResponse<AlertRule[]>(response);
}

export async function getActiveAlerts(): Promise<ActiveAlert[]> {
  const response = await fetch(`${API_BASE}/alerts/active`);
  return handleResponse<ActiveAlert[]>(response);
}

export async function createAlert(alert: AlertRuleCreate): Promise<AlertRule> {
  const response = await fetch(`${API_BASE}/alerts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(alert),
  });
  return handleResponse<AlertRule>(response);
}

export async function updateAlert(
  alertId: number,
  alertUpdate: AlertRuleUpdate
): Promise<AlertRule> {
  const response = await fetch(`${API_BASE}/alerts/${alertId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(alertUpdate),
  });
  return handleResponse<AlertRule>(response);
}

export async function deleteAlert(alertId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/alerts/${alertId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete alert');
  }
}

export async function getAlertHistory(
  alertId: number,
  startTime?: string,
  endTime?: string,
  limit = 100
): Promise<AlertHistory[]> {
  const params: Record<string, unknown> = { limit };
  if (startTime) params.start_time = startTime;
  if (endTime) params.end_time = endTime;

  const queryString = buildQueryString(params);
  const response = await fetch(`${API_BASE}/alerts/${alertId}/history${queryString}`);
  return handleResponse<AlertHistory[]>(response);
}

export async function acknowledgeAlert(alertId: number, notes?: string): Promise<void> {
  const response = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes }),
  });
  if (!response.ok) {
    throw new Error('Failed to acknowledge alert');
  }
}

// ============== System Health API ==============

export async function getSystemHealth(): Promise<SystemHealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  return handleResponse<SystemHealthResponse>(response);
}

export async function getDetailedHealth(): Promise<{
  status: string;
  metrics: Record<string, unknown>;
  last_updated: string;
  active_alerts: number;
  pending_recommendations: number;
  system_metrics: {
    total_collected: number;
    by_type: Record<string, unknown>;
  };
  agent_performance: {
    total_records: number;
    agents_monitored: number;
  };
}> {
  const response = await fetch(`${API_BASE}/health/detailed`);
  return handleResponse(response);
}

// ============== Dashboard Summary API ==============

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await fetch(`${API_BASE}/dashboard/summary`);
  return handleResponse<DashboardSummary>(response);
}