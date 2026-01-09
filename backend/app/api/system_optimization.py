from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.system_optimization_engine import SystemOptimizationEngine
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.system_optimization import (
    SystemMetricsCreate, SystemMetricsResponse,
    AgentPerformanceMetricsCreate, AgentPerformanceMetricsResponse, AgentPerformanceAggregatedStats,
    OptimizationRecommendationCreate, OptimizationRecommendationResponse,
    PerformanceBaselineCreate, PerformanceBaselineResponse, PerformanceBaselineUpdate,
    AlertRuleCreate, AlertRuleResponse, AlertRuleUpdate, AlertHistoryResponse,
    MetricsQueryRequest, MetricsQueryResponse,
    RecommendationApplyRequest,
    SystemHealthResponse, SystemHealthStatus,
    MetricType, AlertCondition, AlertSeverity, RecommendationType, EffortLevel, RecommendationStatus, AggregationType
)

router = APIRouter()


# Initialize engine
def get_optimization_engine(db: AsyncSession = Depends(get_db)) -> SystemOptimizationEngine:
    return SystemOptimizationEngine(db)


# ==================== System Metrics Endpoints ====================

@router.get("/metrics", response_model=List[SystemMetricsResponse])
async def get_system_metrics(
    metric_type: Optional[MetricType] = None,
    metric_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    aggregation: AggregationType = AggregationType.AVG,
    limit: int = Query(default=1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Get system metrics with optional filtering and aggregation"""
    if start_time is None:
        start_time = datetime.utcnow() - timedelta(hours=24)
    if end_time is None:
        end_time = datetime.utcnow()
    
    metrics = await engine.get_metrics(
        metric_type=metric_type,
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time,
        aggregation=aggregation.value,
        limit=limit
    )
    
    return metrics


@router.post("/metrics/query", response_model=List[MetricsQueryResponse])
async def query_metrics(
    query_request: MetricsQueryRequest,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Custom metrics query with aggregation"""
    results = await engine.query_metrics(
        metric_types=query_request.metric_types,
        metric_names=query_request.metric_names,
        start_time=query_request.start_time,
        end_time=query_request.end_time,
        aggregation=query_request.aggregation.value,
        tags=query_request.tags,
        limit=query_request.limit
    )
    
    return results


@router.post("/metrics", response_model=SystemMetricsResponse, status_code=status.HTTP_201_CREATED)
async def create_system_metric(
    metric_data: SystemMetricsCreate,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Collect a new system metric"""
    metric = await engine.collect_metrics(
        metric_type=metric_data.metric_type.value,
        metric_name=metric_data.metric_name,
        value=metric_data.metric_value,
        tags=metric_data.tags
    )
    
    # Check alerts for the new metric
    alerts = await engine.check_alerts(
        metric_type=metric_data.metric_type.value,
        value=metric_data.metric_value
    )
    
    return metric


# ==================== Agent Performance Endpoints ====================

@router.get("/agents/{agent_id}/performance", response_model=AgentPerformanceAggregatedStats)
async def get_agent_performance(
    agent_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Get aggregated performance metrics for a specific agent"""
    if start_time is None:
        start_time = datetime.utcnow() - timedelta(hours=24)
    if end_time is None:
        end_time = datetime.utcnow()
    
    stats = await engine.get_agent_performance(
        agent_id=agent_id,
        start_time=start_time,
        end_time=end_time
    )
    
    return stats


@router.post("/agents/{agent_id}/performance", response_model=AgentPerformanceMetricsResponse, status_code=status.HTTP_201_CREATED)
async def record_agent_performance(
    agent_id: int,
    performance_data: AgentPerformanceMetricsCreate,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Record performance metrics for an agent"""
    metric = await engine.collect_agent_performance(
        agent_id=agent_id,
        execution_time_ms=performance_data.execution_time_ms,
        token_count=performance_data.token_count,
        cost=performance_data.cost,
        success_rate=performance_data.success_rate,
        avg_response_time=performance_data.avg_response_time,
        error_count=performance_data.error_count
    )
    
    return metric


# ==================== Optimization Recommendations Endpoints ====================

@router.get("/recommendations", response_model=List[OptimizationRecommendationResponse])
async def list_recommendations(
    agent_id: Optional[int] = None,
    recommendation_type: Optional[RecommendationType] = None,
    status: Optional[RecommendationStatus] = None,
    impact_score_min: Optional[float] = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """List optimization recommendations with optional filtering"""
    recommendations = await engine.list_recommendations(
        agent_id=agent_id,
        recommendation_type=recommendation_type,
        status=status,
        impact_score_min=impact_score_min,
        limit=limit
    )
    
    return recommendations


@router.post("/recommendations", response_model=OptimizationRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    recommendation_data: OptimizationRecommendationCreate,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Create a new optimization recommendation"""
    recommendation = await engine.create_recommendation(
        agent_id=recommendation_data.agent_id,
        recommendation_type=recommendation_data.recommendation_type.value,
        title=recommendation_data.title,
        description=recommendation_data.description,
        current_value=recommendation_data.current_value,
        recommended_value=recommendation_data.recommended_value,
        impact_score=recommendation_data.impact_score,
        effort_level=recommendation_data.effort_level.value,
        expires_at=recommendation_data.expires_at
    )
    
    return recommendation


@router.post("/recommendations/{recommendation_id}/apply", response_model=OptimizationRecommendationResponse)
async def apply_recommendation(
    recommendation_id: int,
    apply_request: RecommendationApplyRequest,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Apply an optimization recommendation"""
    recommendation = await engine.apply_optimization(
        recommendation_id=recommendation_id,
        auto_approve=apply_request.auto_approve
    )
    
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return recommendation


@router.put("/recommendations/{recommendation_id}/status")
async def update_recommendation_status(
    recommendation_id: int,
    status: RecommendationStatus,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Update recommendation status"""
    recommendation = await engine.update_recommendation_status(
        recommendation_id=recommendation_id,
        status=status.value
    )
    
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return {"message": "Recommendation status updated", "recommendation": recommendation}


@router.get("/recommendations/generate/{agent_id}")
async def generate_recommendations_for_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Generate AI-powered optimization recommendations for an agent"""
    recommendations = await engine.generate_recommendations(agent_id=agent_id)
    
    return {
        "agent_id": agent_id,
        "recommendations_count": len(recommendations),
        "recommendations": recommendations
    }


# ==================== Performance Baselines Endpoints ====================

@router.get("/baselines", response_model=List[PerformanceBaselineResponse])
async def list_baselines(
    agent_id: Optional[int] = None,
    metric_type: Optional[MetricType] = None,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """List performance baselines"""
    baselines = await engine.list_baselines(
        agent_id=agent_id,
        metric_type=metric_type
    )
    
    return baselines


@router.post("/baselines", response_model=PerformanceBaselineResponse, status_code=status.HTTP_201_CREATED)
async def create_baseline(
    baseline_data: PerformanceBaselineCreate,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Create a new performance baseline"""
    baseline = await engine.create_baseline(
        agent_id=baseline_data.agent_id,
        metric_type=baseline_data.metric_type.value,
        baseline_value=baseline_data.baseline_value,
        threshold_value=baseline_data.threshold_value,
        measurement_window=baseline_data.measurement_window
    )
    
    return baseline


@router.put("/baselines/{baseline_id}", response_model=PerformanceBaselineResponse)
async def update_baseline(
    baseline_id: int,
    baseline_update: PerformanceBaselineUpdate,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Update a performance baseline"""
    baseline = await engine.update_baseline(
        baseline_id=baseline_id,
        baseline_value=baseline_update.baseline_value,
        threshold_value=baseline_update.threshold_value,
        measurement_window=baseline_update.measurement_window
    )
    
    if baseline is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baseline not found"
        )
    
    return baseline


@router.delete("/baselines/{baseline_id}")
async def delete_baseline(
    baseline_id: int,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Delete a performance baseline"""
    success = await engine.delete_baseline(baseline_id=baseline_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baseline not found"
        )
    
    return {"message": "Baseline deleted successfully"}


@router.post("/baselines/calculate/{agent_id}")
async def calculate_baseline(
    agent_id: int,
    metric_type: MetricType,
    window: int = Query(default=3600, ge=60, le=86400),
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Calculate baseline for a specific metric"""
    baseline_value = await engine.calculate_baseline(
        agent_id=agent_id,
        metric_type=metric_type.value,
        window=window
    )
    
    return {
        "agent_id": agent_id,
        "metric_type": metric_type.value,
        "window_seconds": window,
        "baseline_value": baseline_value
    }


# ==================== Alert Rules Endpoints ====================

@router.get("/alerts", response_model=List[AlertRuleResponse])
async def list_alerts(
    metric_type: Optional[MetricType] = None,
    severity: Optional[AlertSeverity] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """List alert rules"""
    alerts = await engine.list_alerts(
        metric_type=metric_type,
        severity=severity,
        is_active=is_active
    )
    
    return alerts


@router.get("/alerts/active")
async def get_active_alerts(
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Get currently triggered alerts"""
    alerts = await engine.get_active_alerts()
    
    return alerts


@router.post("/alerts", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Create a new alert rule"""
    alert = await engine.create_alert(
        name=alert_data.name,
        description=alert_data.description,
        metric_type=alert_data.metric_type.value,
        condition=alert_data.condition.value,
        threshold_value=alert_data.threshold_value,
        severity=alert_data.severity.value,
        cooldown_period=alert_data.cooldown_period
    )
    
    return alert


@router.put("/alerts/{alert_id}", response_model=AlertRuleResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Update an alert rule"""
    alert = await engine.update_alert(
        alert_id=alert_id,
        name=alert_update.name,
        description=alert_update.description,
        metric_type=alert_update.metric_type.value if alert_update.metric_type else None,
        condition=alert_update.condition.value if alert_update.condition else None,
        threshold_value=alert_update.threshold_value,
        severity=alert_update.severity.value if alert_update.severity else None,
        is_active=alert_update.is_active,
        cooldown_period=alert_update.cooldown_period
    )
    
    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    return alert


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Delete an alert rule"""
    success = await engine.delete_alert(alert_id=alert_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    return {"message": "Alert rule deleted successfully"}


@router.get("/alerts/{alert_id}/history", response_model=List[AlertHistoryResponse])
async def get_alert_history(
    alert_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Get alert history for a specific alert rule"""
    if start_time is None:
        start_time = datetime.utcnow() - timedelta(days=7)
    if end_time is None:
        end_time = datetime.utcnow()
    
    history = await engine.get_alert_history(
        alert_id=alert_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )
    
    return history


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Acknowledge an active alert"""
    success = await engine.acknowledge_alert(
        alert_id=alert_id,
        acknowledged_by=current_user.username,
        notes=notes
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active alert not found"
        )
    
    return {"message": "Alert acknowledged successfully"}


# ==================== System Health Endpoints ====================

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Get overall system health status"""
    health = await engine.get_system_health()
    
    return health


@router.get("/health/detailed")
async def get_detailed_health(
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Get detailed system health information"""
    health = await engine.get_detailed_health()
    
    return health


# ==================== Dashboard Summary Endpoints ====================

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    engine: SystemOptimizationEngine = Depends(get_optimization_engine)
):
    """Get dashboard summary with key metrics and recommendations"""
    summary = await engine.get_dashboard_summary()
    
    return summary