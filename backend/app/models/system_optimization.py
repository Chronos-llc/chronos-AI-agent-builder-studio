from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import ENUM
import enum
from datetime import datetime

from app.models.base import BaseModel


class MetricType(enum.Enum):
    CPU = "CPU"
    MEMORY = "MEMORY"
    DISK = "DISK"
    NETWORK = "NETWORK"
    RESPONSE_TIME = "RESPONSE_TIME"
    THROUGHPUT = "THROUGHPUT"


class AlertCondition(enum.Enum):
    GT = "GT"  # Greater than
    LT = "LT"  # Less than
    EQ = "EQ"  # Equal to
    GTE = "GTE"  # Greater than or equal
    LTE = "LTE"  # Less than or equal


class AlertSeverity(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendationType(enum.Enum):
    PERFORMANCE = "PERFORMANCE"
    COST = "COST"
    RELIABILITY = "RELIABILITY"
    SCALABILITY = "SCALABILITY"


class EffortLevel(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendationStatus(enum.Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    DISMISSED = "DISMISSED"
    EXPIRED = "EXPIRED"


class SystemMetrics(BaseModel):
    __tablename__ = "system_metrics"
    
    metric_type = Column(Enum(MetricType), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)
    tags = Column(JSON, nullable=True)  # Additional tags for filtering
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<SystemMetrics(id={self.id}, metric_type='{self.metric_type}', metric_name='{self.metric_name}', value={self.metric_value})>"


class AgentPerformanceMetrics(BaseModel):
    __tablename__ = "agent_performance_metrics"
    
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    execution_time_ms = Column(Float, nullable=True)
    token_count = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)
    avg_response_time = Column(Float, nullable=True)
    error_count = Column(Integer, default=0)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="performance_metrics")
    
    def __repr__(self):
        return f"<AgentPerformanceMetrics(id={self.id}, agent_id={self.agent_id}, execution_time_ms={self.execution_time_ms})>"


class OptimizationRecommendation(BaseModel):
    __tablename__ = "optimization_recommendations"
    
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    recommendation_type = Column(Enum(RecommendationType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    current_value = Column(String(100), nullable=True)
    recommended_value = Column(String(100), nullable=True)
    impact_score = Column(Float, nullable=False)  # 0-1 score
    effort_level = Column(Enum(EffortLevel), nullable=False)
    status = Column(Enum(RecommendationStatus), default=RecommendationStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="optimization_recommendations")
    
    def __repr__(self):
        return f"<OptimizationRecommendation(id={self.id}, title='{self.title}', type='{self.recommendation_type}')>"


class PerformanceBaseline(BaseModel):
    __tablename__ = "performance_baselines"
    
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    metric_type = Column(Enum(MetricType), nullable=False, index=True)
    baseline_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=True)
    measurement_window = Column(Integer, default=3600, nullable=False)  # Window in seconds
    
    # Relationships
    agent = relationship("AgentModel", back_populates="performance_baselines")
    
    def __repr__(self):
        return f"<PerformanceBaseline(id={self.id}, metric_type='{self.metric_type}', baseline_value={self.baseline_value})>"


class AlertRule(BaseModel):
    __tablename__ = "alert_rules"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    metric_type = Column(Enum(MetricType), nullable=False, index=True)
    condition = Column(Enum(AlertCondition), nullable=False)
    threshold_value = Column(Float, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    cooldown_period = Column(Integer, default=300, nullable=False)  # Cooldown in seconds
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    alert_history = relationship("AlertHistory", back_populates="alert_rule", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.name}', severity='{self.severity}')>"


class AlertHistory(BaseModel):
    __tablename__ = "alert_history"
    
    alert_rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False, index=True)
    triggered_value = Column(Float, nullable=False)
    triggered_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    alert_rule = relationship("AlertRule", back_populates="alert_history")
    
    def __repr__(self):
        return f"<AlertHistory(id={self.id}, alert_rule_id={self.alert_rule_id}, triggered_at='{self.triggered_at}')>"