from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class MetricType(str, Enum):
    CPU = "CPU"
    MEMORY = "MEMORY"
    DISK = "DISK"
    NETWORK = "NETWORK"
    RESPONSE_TIME = "RESPONSE_TIME"
    THROUGHPUT = "THROUGHPUT"


class AlertCondition(str, Enum):
    GT = "GT"
    LT = "LT"
    EQ = "EQ"
    GTE = "GTE"
    LTE = "LTE"


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendationType(str, Enum):
    PERFORMANCE = "PERFORMANCE"
    COST = "COST"
    RELIABILITY = "RELIABILITY"
    SCALABILITY = "SCALABILITY"


class EffortLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendationStatus(str, Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    DISMISSED = "DISMISSED"
    EXPIRED = "EXPIRED"


class AggregationType(str, Enum):
    AVG = "avg"
    SUM = "sum"
    MAX = "max"
    MIN = "min"


# System Metrics Schemas
class SystemMetricsBase(BaseModel):
    metric_type: MetricType
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    unit: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class SystemMetricsCreate(SystemMetricsBase):
    pass


class SystemMetricsResponse(SystemMetricsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Agent Performance Metrics Schemas
class AgentPerformanceMetricsBase(BaseModel):
    agent_id: int
    execution_time_ms: Optional[float] = None
    token_count: Optional[int] = None
    cost: Optional[float] = None
    success_rate: Optional[float] = None
    avg_response_time: Optional[float] = None
    error_count: int = 0
    timestamp: Optional[datetime] = None


class AgentPerformanceMetricsCreate(AgentPerformanceMetricsBase):
    pass


class AgentPerformanceMetricsResponse(AgentPerformanceMetricsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AgentPerformanceAggregatedStats(BaseModel):
    """Aggregated statistics for agent performance over a time period"""
    agent_id: int
    total_executions: int
    avg_execution_time_ms: Optional[float] = None
    max_execution_time_ms: Optional[float] = None
    min_execution_time_ms: Optional[float] = None
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    avg_success_rate: Optional[float] = None
    total_errors: int
    avg_response_time_ms: Optional[float] = None


# Optimization Recommendation Schemas
class OptimizationRecommendationBase(BaseModel):
    agent_id: Optional[int] = None
    recommendation_type: RecommendationType
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    current_value: Optional[str] = None
    recommended_value: Optional[str] = None
    impact_score: float = Field(..., ge=0, le=1)
    effort_level: EffortLevel
    status: RecommendationStatus = RecommendationStatus.PENDING


class OptimizationRecommendationCreate(OptimizationRecommendationBase):
    pass


class OptimizationRecommendationResponse(OptimizationRecommendationBase):
    id: int
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecommendationApplyRequest(BaseModel):
    apply_changes: bool = False
    auto_approve: bool = False
    notes: Optional[str] = None


# Performance Baseline Schemas
class PerformanceBaselineBase(BaseModel):
    agent_id: Optional[int] = None
    metric_type: MetricType
    baseline_value: float
    threshold_value: Optional[float] = None
    measurement_window: int = Field(default=3600, ge=60)


class PerformanceBaselineCreate(PerformanceBaselineBase):
    pass


class PerformanceBaselineResponse(PerformanceBaselineBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PerformanceBaselineUpdate(BaseModel):
    baseline_value: Optional[float] = None
    threshold_value: Optional[float] = None
    measurement_window: Optional[int] = None


# Alert Rule Schemas
class AlertRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    metric_type: MetricType
    condition: AlertCondition
    threshold_value: float
    severity: AlertSeverity
    is_active: bool = True
    cooldown_period: int = Field(default=300, ge=0)


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleResponse(AlertRuleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    metric_type: Optional[MetricType] = None
    condition: Optional[AlertCondition] = None
    threshold_value: Optional[float] = None
    severity: Optional[AlertSeverity] = None
    is_active: Optional[bool] = None
    cooldown_period: Optional[int] = None


class AlertHistoryResponse(BaseModel):
    id: int
    alert_rule_id: int
    triggered_value: float
    triggered_at: datetime
    acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# Metrics Query Schemas
class MetricsQueryRequest(BaseModel):
    metric_types: Optional[List[MetricType]] = None
    metric_names: Optional[List[str]] = None
    start_time: datetime
    end_time: datetime
    aggregation: AggregationType = AggregationType.AVG
    tags: Optional[Dict[str, Any]] = None
    limit: int = Field(default=1000, ge=1, le=10000)


class MetricsQueryResponse(BaseModel):
    """Response for metrics query with time-series data"""
    metric_type: MetricType
    metric_name: str
    aggregation: str
    start_time: datetime
    end_time: datetime
    data_points: List[Dict[str, Any]]  # List of {timestamp, value} objects
    statistics: Optional[Dict[str, float]] = None  # {avg, sum, max, min, count}


# System Health Schemas
class SystemHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class SystemHealthResponse(BaseModel):
    status: SystemHealthStatus
    metrics: Dict[str, Any]
    last_updated: datetime
    active_alerts: int = 0
    pending_recommendations: int = 0


# Dashboard Summary Schemas
class DashboardSummary(BaseModel):
    system_health: SystemHealthResponse
    recent_metrics: List[SystemMetricsResponse]
    top_recommendations: List[OptimizationRecommendationResponse]
    active_alerts: List[AlertRuleResponse]