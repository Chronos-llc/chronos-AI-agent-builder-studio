from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from backend.app.models.base import Base

class TrainingSessionStatus(PyEnum):
    active = 'active'
    completed = 'completed'
    paused = 'paused'

class TrainingMode(PyEnum):
    standard = 'standard'
    advanced = 'advanced'
    evaluation = 'evaluation'

class CorrectionType(PyEnum):
    response = 'response'
    behavior = 'behavior'
    knowledge = 'knowledge'

class TrainingSession(Base):
    __tablename__ = 'training_sessions'
    
    id = Column(String(64), primary_key=True, index=True)
    agent_id = Column(String(64), ForeignKey('agents.id'), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    status = Column(Enum(TrainingSessionStatus), default=TrainingSessionStatus.active)
    training_mode = Column(Enum(TrainingMode), default=TrainingMode.standard)
    
    interactions = relationship('TrainingInteraction', back_populates='session', cascade='all, delete-orphan')
    corrections = relationship('TrainingCorrection', back_populates='session', cascade='all, delete-orphan')

class TrainingInteraction(Base):
    __tablename__ = 'training_interactions'
    
    id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey('training_sessions.id'), nullable=False)
    user_input = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    feedback = Column(Text, nullable=True)
    
    session = relationship('TrainingSession', back_populates='interactions')
    corrections = relationship('TrainingCorrection', back_populates='interaction', cascade='all, delete-orphan')

class TrainingCorrection(Base):
    __tablename__ = 'training_corrections'
    
    id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey('training_sessions.id'), nullable=False)
    interaction_id = Column(String(64), ForeignKey('training_interactions.id'), nullable=False)
    correction_type = Column(Enum(CorrectionType), nullable=False)
    content = Column(Text, nullable=False)
    applied_at = Column(DateTime, server_default=func.now())
    applied_by = Column(String(64), nullable=True)
    
    session = relationship('TrainingSession', back_populates='corrections')
    interaction = relationship('TrainingInteraction', back_populates='corrections')