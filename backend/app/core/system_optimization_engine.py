"""
System Optimization Engine

This module provides the core engine for system optimization, performance monitoring,
and automated tuning capabilities.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, asc
from sqlalchemy.future import select

from app.models.system_optimization import (
    SystemMetrics, AgentPerformanceMetrics, OptimizationRecommendation,
    PerformanceBaseline, AlertRule, AlertHistory,
    MetricType, AlertCondition, AlertSeverity, RecommendationType, EffortLevel, RecommendationStatus
)

logger = logging.getLogger(__name__)


class SystemOptimizationEngine:
    """
    Core engine for system optimization and performance monitoring.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== Metrics Collection ====================
    
    async def collect_metrics(
        self,
        metric_type: str,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, Any]] = None
    ) -> SystemMetrics:
        """Collect a new system metric"""
        metric = SystemMetrics(
            metric_type=MetricType(metric_type),
            metric_name=metric_name,
            metric_value=value,
            tags=tags,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        
        logger.info(f"Collected metric: {metric_type}.{metric_name} = {value}")
        return metric
    
    async def get_metrics(
        self,
        metric_type: Optional[str] = None,
        metric_name: Optional[str] = None,
        start_time: datetime = None,
        end_time: datetime = None,
        aggregation: str = "avg",
        limit: int = 1000
    ) -> List[SystemMetrics]:
        """Get system metrics with filtering and aggregation"""
        query = select(SystemMetrics)
        
        if metric_type:
            query = query.where(SystemMetrics.metric_type == MetricType(metric_type))
        if metric_name:
            query = query.where(SystemMetrics.metric_name == metric_name)
        if start_time:
            query = query.where(SystemMetrics.timestamp >= start_time)
        if end_time:
            query = query.where(SystemMetrics.timestamp <= end_time)
        
        query = query.order_by(desc(SystemMetrics.timestamp)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def query_metrics(
        self,
        metric_types: Optional[List[str]] = None,
        metric_names: Optional[List[str]] = None,
        start_time: datetime = None,
        end_time: datetime = None,
        aggregation: str = "avg",
        tags: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Custom metrics query with aggregation"""
        results = []
        
        if metric_types is None:
            metric_types = [mt.value for mt in MetricType]
        
        for mt in metric_types:
            query = select(SystemMetrics).where(
                and_(
                    SystemMetrics.metric_type == MetricType(mt),
                    SystemMetrics.timestamp >= start_time,
                    SystemMetrics.timestamp <= end_time
                )
            )
            
            if metric_names:
                query = query.where(SystemMetrics.metric_name.in_(metric_names))
            
            query = query.order_by(desc(SystemMetrics.timestamp)).limit(limit)
            
            result = await self.db.execute(query)
            metrics = result.scalars().all()
            
            if metrics:
                # Calculate aggregation
                values = [m.metric_value for m in metrics]
                if aggregation == "avg":
                    agg_value = sum(values) / len(values)
                elif aggregation == "sum":
                    agg_value = sum(values)
                elif aggregation == "max":
                    agg_value = max(values)
                elif aggregation == "min":
                    agg_value = min(values)
                else:
                    agg_value = sum(values) / len(values)
                
                data_points = [
                    {"timestamp": m.timestamp.isoformat(), "value": m.metric_value}
                    for m in metrics
                ]
                
                results.append({
                    "metric_type": MetricType(mt),
                    "metric_name": metrics[0].metric_name if metrics else "",
                    "aggregation": aggregation,
                    "start_time": start_time,
                    "end_time": end_time,
                    "data_points": data_points,
                    "statistics": {
                        "avg": sum(values) / len(values),
                        "sum": sum(values),
                        "max": max(values),
                        "min": min(values),
                        "count": len(values)
                    }
                })
        
        return results
    
    # ==================== Agent Performance ====================
    
    async def collect_agent_performance(
        self,
        agent_id: int,
        execution_time_ms: Optional[float] = None,
        token_count: Optional[int] = None,
        cost: Optional[float] = None,
        success_rate: Optional[float] = None,
        avg_response_time: Optional[float] = None,
        error_count: int = 0
    ) -> AgentPerformanceMetrics:
        """Collect performance metrics for an agent"""
        metric = AgentPerformanceMetrics(
            agent_id=agent_id,
            execution_time_ms=execution_time_ms,
            token_count=token_count,
            cost=cost,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            error_count=error_count,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        
        logger.info(f"Collected agent performance for agent_id={agent_id}")
        return metric
    
    async def get_agent_performance(
        self,
        agent_id: int,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> Dict[str, Any]:
        """Get aggregated performance metrics for an agent"""
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if end_time is None:
            end_time = datetime.utcnow()
        
        query = select(AgentPerformanceMetrics).where(
            and_(
                AgentPerformanceMetrics.agent_id == agent_id,
                AgentPerformanceMetrics.timestamp >= start_time,
                AgentPerformanceMetrics.timestamp <= end_time
            )
        )
        
        result = await self.db.execute(query)
        metrics = result.scalars().all()
        
        if not metrics:
            return {
                "agent_id": agent_id,
                "total_executions": 0,
                "avg_execution_time_ms": None,
                "max_execution_time_ms": None,
                "min_execution_time_ms": None,
                "total_tokens": None,
                "total_cost": None,
                "avg_success_rate": None,
                "total_errors": 0,
                "avg_response_time_ms": None
            }
        
        execution_times = [m.execution_time_ms for m in metrics if m.execution_time_ms is not None]
        token_counts = [m.token_count for m in metrics if m.token_count is not None]
        costs = [m.cost for m in metrics if m.cost is not None]
        success_rates = [m.success_rate for m in metrics if m.success_rate is not None]
        response_times = [m.avg_response_time for m in metrics if m.avg_response_time is not None]
        errors = [m.error_count for m in metrics]
        
        return {
            "agent_id": agent_id,
            "total_executions": len(metrics),
            "avg_execution_time_ms": sum(execution_times) / len(execution_times) if execution_times else None,
            "max_execution_time_ms": max(execution_times) if execution_times else None,
            "min_execution_time_ms": min(execution_times) if execution_times else None,
            "total_tokens": sum(token_counts) if token_counts else None,
            "total_cost": sum(costs) if costs else None,
            "avg_success_rate": sum(success_rates) / len(success_rates) if success_rates else None,
            "total_errors": sum(errors),
            "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else None
        }
    
    # ==================== Recommendations ====================
    
    async def list_recommendations(
        self,
        agent_id: Optional[int] = None,
        recommendation_type: Optional[str] = None,
        status: Optional[str] = None,
        impact_score_min: Optional[float] = None,
        limit: int = 50
    ) -> List[OptimizationRecommendation]:
        """List optimization recommendations with filtering"""
        query = select(OptimizationRecommendation)
        
        if agent_id:
            query = query.where(OptimizationRecommendation.agent_id == agent_id)
        if recommendation_type:
            query = query.where(OptimizationRecommendation.recommendation_type == RecommendationType(recommendation_type))
        if status:
            query = query.where(OptimizationRecommendation.status == RecommendationStatus(status))
        if impact_score_min is not None:
            query = query.where(OptimizationRecommendation.impact_score >= impact_score_min)
        
        query = query.order_by(desc(OptimizationRecommendation.impact_score)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_recommendation(
        self,
        agent_id: Optional[int],
        recommendation_type: str,
        title: str,
        description: str,
        current_value: Optional[str],
        recommended_value: Optional[str],
        impact_score: float,
        effort_level: str,
        expires_at: Optional[datetime] = None
    ) -> OptimizationRecommendation:
        """Create a new optimization recommendation"""
        recommendation = OptimizationRecommendation(
            agent_id=agent_id,
            recommendation_type=RecommendationType(recommendation_type),
            title=title,
            description=description,
            current_value=current_value,
            recommended_value=recommended_value,
            impact_score=impact_score,
            effort_level=EffortLevel(effort_level),
            expires_at=expires_at
        )
        
        self.db.add(recommendation)
        await self.db.commit()
        await self.db.refresh(recommendation)
        
        logger.info(f"Created recommendation: {title}")
        return recommendation
    
    async def apply_optimization(
        self,
        recommendation_id: int,
        auto_approve: bool = False
    ) -> Optional[OptimizationRecommendation]:
        """Apply an optimization recommendation"""
        result = await self.db.execute(
            select(OptimizationRecommendation).where(
                OptimizationRecommendation.id == recommendation_id
            )
        )
        recommendation = result.scalar_one_or_none()
        
        if not recommendation:
            return None
        
        # Update recommendation status
        recommendation.status = RecommendationStatus.APPLIED
        
        await self.db.commit()
        await self.db.refresh(recommendation)
        
        logger.info(f"Applied recommendation: {recommendation.title}")
        return recommendation
    
    async def update_recommendation_status(
        self,
        recommendation_id: int,
        status: str
    ) -> Optional[OptimizationRecommendation]:
        """Update recommendation status"""
        result = await self.db.execute(
            select(OptimizationRecommendation).where(
                OptimizationRecommendation.id == recommendation_id
            )
        )
        recommendation = result.scalar_one_or_none()
        
        if not recommendation:
            return None
        
        recommendation.status = RecommendationStatus(status)
        
        await self.db.commit()
        await self.db.refresh(recommendation)
        
        return recommendation
    
    async def generate_recommendations(self, agent_id: int) -> List[Dict[str, Any]]:
        """Generate AI-powered optimization recommendations for an agent"""
        # Get current performance metrics
        performance = await self.get_agent_performance(agent_id)
        
        recommendations = []
        
        # Generate recommendations based on performance metrics
        if performance["avg_execution_time_ms"] and performance["avg_execution_time_ms"] > 5000:
            recommendations.append({
                "type": "PERFORMANCE",
                "title": "High Execution Time Detected",
                "description": f"Average execution time is {performance['avg_execution_time_ms']:.2f}ms. Consider optimizing prompts or using a faster model.",
                "impact_score": 0.8,
                "effort_level": "MEDIUM"
            })
        
        if performance["avg_success_rate"] and performance["avg_success_rate"] < 0.9:
            recommendations.append({
                "type": "RELIABILITY",
                "title": "Low Success Rate",
                "description": f"Success rate is {performance['avg_success_rate']*100:.1f}%. Review error patterns and improve error handling.",
                "impact_score": 0.9,
                "effort_level": "HIGH"
            })
        
        if performance["total_cost"] and performance["total_cost"] > 100:
            recommendations.append({
                "type": "COST",
                "title": "High API Costs",
                "description": f"Total cost is ${performance['total_cost']:.2f}. Consider using a more cost-effective model.",
                "impact_score": 0.7,
                "effort_level": "MEDIUM"
            })
        
        return recommendations
    
    # ==================== Performance Baselines ====================
    
    async def list_baselines(
        self,
        agent_id: Optional[int] = None,
        metric_type: Optional[str] = None
    ) -> List[PerformanceBaseline]:
        """List performance baselines"""
        query = select(PerformanceBaseline)
        
        if agent_id:
            query = query.where(PerformanceBaseline.agent_id == agent_id)
        if metric_type:
            query = query.where(PerformanceBaseline.metric_type == MetricType(metric_type))
        
        query = query.order_by(PerformanceBaseline.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_baseline(
        self,
        agent_id: Optional[int],
        metric_type: str,
        baseline_value: float,
        threshold_value: Optional[float] = None,
        measurement_window: int = 3600
    ) -> PerformanceBaseline:
        """Create a new performance baseline"""
        baseline = PerformanceBaseline(
            agent_id=agent_id,
            metric_type=MetricType(metric_type),
            baseline_value=baseline_value,
            threshold_value=threshold_value,
            measurement_window=measurement_window
        )
        
        self.db.add(baseline)
        await self.db.commit()
        await self.db.refresh(baseline)
        
        logger.info(f"Created baseline: {metric_type} = {baseline_value}")
        return baseline
    
    async def update_baseline(
        self,
        baseline_id: int,
        baseline_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
        measurement_window: Optional[int] = None
    ) -> Optional[PerformanceBaseline]:
        """Update a performance baseline"""
        result = await self.db.execute(
            select(PerformanceBaseline).where(PerformanceBaseline.id == baseline_id)
        )
        baseline = result.scalar_one_or_none()
        
        if not baseline:
            return None
        
        if baseline_value is not None:
            baseline.baseline_value = baseline_value
        if threshold_value is not None:
            baseline.threshold_value = threshold_value
        if measurement_window is not None:
            baseline.measurement_window = measurement_window
        
        await self.db.commit()
        await self.db.refresh(baseline)
        
        return baseline
    
    async def delete_baseline(self, baseline_id: int) -> bool:
        """Delete a performance baseline"""
        result = await self.db.execute(
            select(PerformanceBaseline).where(PerformanceBaseline.id == baseline_id)
        )
        baseline = result.scalar_one_or_none()
        
        if not baseline:
            return False
        
        await self.db.delete(baseline)
        await self.db.commit()
        
        return True
    
    async def calculate_baseline(
        self,
        agent_id: int,
        metric_type: str,
        window: int = 3600
    ) -> Optional[float]:
        """Calculate baseline for a specific metric"""
        start_time = datetime.utcnow() - timedelta(seconds=window)
        
        query = select(SystemMetrics).where(
            and_(
                SystemMetrics.metric_type == MetricType(metric_type),
                SystemMetrics.timestamp >= start_time
            )
        )
        
        result = await self.db.execute(query)
        metrics = result.scalars().all()
        
        if not metrics:
            return None
        
        values = [m.metric_value for m in metrics]
        return sum(values) / len(values)
    
    # ==================== Alert Rules ====================
    
    async def list_alerts(
        self,
        metric_type: Optional[str] = None,
        severity: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[AlertRule]:
        """List alert rules"""
        query = select(AlertRule)
        
        if metric_type:
            query = query.where(AlertRule.metric_type == MetricType(metric_type))
        if severity:
            query = query.where(AlertRule.severity == AlertSeverity(severity))
        if is_active is not None:
            query = query.where(AlertRule.is_active == is_active)
        
        query = query.order_by(AlertRule.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts that have been triggered"""
        # Get recent unacknowledged alert history
        query = select(AlertHistory).where(
            and_(
                AlertHistory.acknowledged == False,
                AlertHistory.triggered_at >= datetime.utcnow() - timedelta(hours=24)
            )
        ).order_by(desc(AlertHistory.triggered_at))
        
        result = await self.db.execute(query)
        history = result.scalars().all()
        
        alerts = []
        for h in history:
            result = await self.db.execute(
                select(AlertRule).where(AlertRule.id == h.alert_rule_id)
            )
            rule = result.scalar_one_or_none()
            if rule and rule.is_active:
                alerts.append({
                    "alert_rule_id": h.alert_rule_id,
                    "alert_rule_name": rule.name,
                    "triggered_value": h.triggered_value,
                    "triggered_at": h.triggered_at.isoformat(),
                    "severity": rule.severity.value,
                    "condition": f"{rule.condition.value} {rule.threshold_value}"
                })
        
        return alerts
    
    async def create_alert(
        self,
        name: str,
        description: Optional[str],
        metric_type: str,
        condition: str,
        threshold_value: float,
        severity: str,
        cooldown_period: int = 300
    ) -> AlertRule:
        """Create a new alert rule"""
        alert = AlertRule(
            name=name,
            description=description,
            metric_type=MetricType(metric_type),
            condition=AlertCondition(condition),
            threshold_value=threshold_value,
            severity=AlertSeverity(severity),
            cooldown_period=cooldown_period
        )
        
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        
        logger.info(f"Created alert rule: {name}")
        return alert
    
    async def update_alert(
        self,
        alert_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metric_type: Optional[str] = None,
        condition: Optional[str] = None,
        threshold_value: Optional[float] = None,
        severity: Optional[str] = None,
        is_active: Optional[bool] = None,
        cooldown_period: Optional[int] = None
    ) -> Optional[AlertRule]:
        """Update an alert rule"""
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return None
        
        if name is not None:
            alert.name = name
        if description is not None:
            alert.description = description
        if metric_type is not None:
            alert.metric_type = MetricType(metric_type)
        if condition is not None:
            alert.condition = AlertCondition(condition)
        if threshold_value is not None:
            alert.threshold_value = threshold_value
        if severity is not None:
            alert.severity = AlertSeverity(severity)
        if is_active is not None:
            alert.is_active = is_active
        if cooldown_period is not None:
            alert.cooldown_period = cooldown_period
        
        await self.db.commit()
        await self.db.refresh(alert)
        
        return alert
    
    async def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert rule"""
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return False
        
        await self.db.delete(alert)
        await self.db.commit()
        
        return True
    
    async def check_alerts(self, metric_type: str, value: float) -> List[Dict[str, Any]]:
        """Check if a metric value triggers any alerts"""
        triggered_alerts = []
        
        query = select(AlertRule).where(
            and_(
                AlertRule.metric_type == MetricType(metric_type),
                AlertRule.is_active == True
            )
        )
        
        result = await self.db.execute(query)
        rules = result.scalars().all()
        
        for rule in rules:
            triggered = False
            
            if rule.condition == AlertCondition.GT and value > rule.threshold_value:
                triggered = True
            elif rule.condition == AlertCondition.LT and value < rule.threshold_value:
                triggered = True
            elif rule.condition == AlertCondition.EQ and value == rule.threshold_value:
                triggered = True
            elif rule.condition == AlertCondition.GTE and value >= rule.threshold_value:
                triggered = True
            elif rule.condition == AlertCondition.LTE and value <= rule.threshold_value:
                triggered = True
            
            if triggered:
                # Check cooldown period
                history_query = select(AlertHistory).where(
                    and_(
                        AlertHistory.alert_rule_id == rule.id,
                        AlertHistory.triggered_at >= datetime.utcnow() - timedelta(seconds=rule.cooldown_period)
                    )
                ).order_by(desc(AlertHistory.triggered_at))
                
                history_result = await self.db.execute(history_query)
                recent_history = history_result.scalars().first()
                
                if recent_history:
                    continue  # Skip due to cooldown
                
                # Create alert history
                alert_history = AlertHistory(
                    alert_rule_id=rule.id,
                    triggered_value=value
                )
                self.db.add(alert_history)
                await self.db.commit()
                
                triggered_alerts.append({
                    "alert_rule_id": rule.id,
                    "name": rule.name,
                    "severity": rule.severity.value,
                    "triggered_value": value,
                    "threshold": rule.threshold_value,
                    "condition": rule.condition.value
                })
        
        return triggered_alerts
    
    async def get_alert_history(
        self,
        alert_id: int,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 100
    ) -> List[AlertHistory]:
        """Get alert history for a specific alert rule"""
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(days=7)
        if end_time is None:
            end_time = datetime.utcnow()
        
        query = select(AlertHistory).where(
            and_(
                AlertHistory.alert_rule_id == alert_id,
                AlertHistory.triggered_at >= start_time,
                AlertHistory.triggered_at <= end_time
            )
        ).order_by(desc(AlertHistory.triggered_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def acknowledge_alert(
        self,
        alert_id: int,
        acknowledged_by: str,
        notes: Optional[str] = None
    ) -> bool:
        """Acknowledge the most recent unacknowledged alert for a rule"""
        query = select(AlertHistory).where(
            and_(
                AlertHistory.alert_rule_id == alert_id,
                AlertHistory.acknowledged == False
            )
        ).order_by(desc(AlertHistory.triggered_at)).limit(1)
        
        result = await self.db.execute(query)
        alert = result.scalar_one_or_none()
        
        if not alert:
            return False
        
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by
        alert.notes = notes
        
        await self.db.commit()
        
        return True
    
    # ==================== System Health ====================
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        # Get recent metrics
        query = select(SystemMetrics).order_by(
            desc(SystemMetrics.timestamp)
        ).limit(100)
        
        result = await self.db.execute(query)
        metrics = result.scalars().all()
        
        # Check for any critical alerts
        active_alerts = await self.get_active_alerts()
        
        # Calculate health based on metrics and alerts
        health_status = "healthy"
        health_metrics = {}
        
        if active_alerts:
            critical_alerts = [a for a in active_alerts if a["severity"] == "CRITICAL"]
            high_alerts = [a for a in active_alerts if a["severity"] == "HIGH"]
            
            if critical_alerts:
                health_status = "unhealthy"
            elif high_alerts:
                health_status = "degraded"
            elif active_alerts:
                health_status = "degraded"
        
        # Group metrics by type
        metrics_by_type = defaultdict(list)
        for m in metrics:
            metrics_by_type[m.metric_type.value].append(m.metric_value)
        
        for metric_type, values in metrics_by_type.items():
            if values:
                health_metrics[metric_type] = {
                    "latest": values[0],
                    "avg": sum(values) / len(values),
                    "max": max(values)
                }
        
        # Count pending recommendations
        query = select(func.count(OptimizationRecommendation.id)).where(
            OptimizationRecommendation.status == RecommendationStatus.PENDING
        )
        result = await self.db.execute(query)
        pending_count = result.scalar_one() or 0
        
        return {
            "status": health_status,
            "metrics": health_metrics,
            "last_updated": datetime.utcnow().isoformat(),
            "active_alerts": len(active_alerts),
            "pending_recommendations": pending_count
        }
    
    async def get_detailed_health(self) -> Dict[str, Any]:
        """Get detailed system health information"""
        health = await self.get_system_health()
        
        # Get system-wide metrics
        query = select(SystemMetrics).order_by(
            desc(SystemMetrics.timestamp)
        ).limit(1000)
        
        result = await self.db.execute(query)
        metrics = result.scalars().all()
        
        # Get performance data
        query = select(AgentPerformanceMetrics).order_by(
            desc(AgentPerformanceMetrics.timestamp)
        ).limit(100)
        
        result = await self.db.execute(query)
        perf_metrics = result.scalars().all()
        
        health["system_metrics"] = {
            "total_collected": len(metrics),
            "by_type": {}
        }
        
        for m in metrics:
            if m.metric_type.value not in health["system_metrics"]["by_type"]:
                health["system_metrics"]["by_type"][m.metric_type.value] = []
            health["system_metrics"]["by_type"][m.metric_type.value].append({
                "name": m.metric_name,
                "value": m.metric_value,
                "timestamp": m.timestamp.isoformat()
            })
        
        health["agent_performance"] = {
            "total_records": len(perf_metrics),
            "agents_monitored": len(set(m.agent_id for m in perf_metrics))
        }
        
        return health
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary with key metrics and recommendations"""
        # Get system health
        health = await self.get_system_health()
        
        # Get recent metrics
        query = select(SystemMetrics).order_by(
            desc(SystemMetrics.timestamp)
        ).limit(20)
        
        result = await self.db.execute(query)
        recent_metrics = result.scalars().all()
        
        # Get top recommendations
        recommendations = await self.list_recommendations(limit=5)
        
        # Get active alerts
        active_alerts = await self.get_active_alerts()
        
        return {
            "system_health": health,
            "recent_metrics": [
                {
                    "id": m.id,
                    "metric_type": m.metric_type.value,
                    "metric_name": m.metric_name,
                    "metric_value": m.metric_value,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in recent_metrics
            ],
            "top_recommendations": [
                {
                    "id": r.id,
                    "title": r.title,
                    "recommendation_type": r.recommendation_type.value,
                    "impact_score": r.impact_score,
                    "effort_level": r.effort_level.value,
                    "status": r.status.value
                }
                for r in recommendations
            ],
            "active_alerts": active_alerts,
            "generated_at": datetime.utcnow().isoformat()
        }