from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TrainingSessionStatus(str, Enum):
    active = 'active'
    completed = 'completed'
    paused = 'paused'

class TrainingMode(str, Enum):
    standard = 'standard'
    advanced = 'advanced'
    evaluation = 'evaluation'

class CorrectionType(str, Enum):
    response = 'response'
    behavior = 'behavior'
    knowledge = 'knowledge'

class TrainingSessionCreate(BaseModel):
    agent_id: str = Field(..., description='ID of the agent being trained')
    training_mode: TrainingMode = Field(default=TrainingMode.standard, description='Training mode')

class TrainingSessionUpdate(BaseModel):
    status: Optional[TrainingSessionStatus] = Field(None, description='Updated status of the training session')
    training_mode: Optional[TrainingMode] = Field(None, description='Updated training mode')

class TrainingSessionResponse(BaseModel):
    id: str
    agent_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    status: TrainingSessionStatus
    training_mode: TrainingMode
    
    class Config:
        from_attributes = True

class TrainingInteractionCreate(BaseModel):
    session_id: str = Field(..., description='ID of the training session')
    user_input: str = Field(..., description='User input during training')
    agent_response: str = Field(..., description='Agent response during training')
    feedback: Optional[str] = Field(None, description='Feedback on the interaction')

class TrainingInteractionResponse(BaseModel):
    id: str
    session_id: str
    user_input: str
    agent_response: str
    timestamp: datetime
    feedback: Optional[str]
    
    class Config:
        from_attributes = True

class TrainingCorrectionCreate(BaseModel):
    session_id: str = Field(..., description='ID of the training session')
    interaction_id: str = Field(..., description='ID of the training interaction')
    correction_type: CorrectionType = Field(..., description='Type of correction')
    content: str = Field(..., description='Correction content')
    applied_by: Optional[str] = Field(None, description='User who applied the correction')

class TrainingCorrectionUpdate(BaseModel):
    correction_type: Optional[CorrectionType] = Field(None, description='Updated type of correction')
    content: Optional[str] = Field(None, description='Updated correction content')
    status: Optional[str] = Field(None, description='Updated status of the correction')

class TrainingCorrectionResponse(BaseModel):
    id: str
    session_id: str
    interaction_id: str
    correction_type: CorrectionType
    content: str
    applied_at: datetime
    applied_by: Optional[str]
    
    class Config:
        from_attributes = True

class TrainingTestRequest(BaseModel):
    session_id: Optional[str] = Field(None, description='ID of the training session')
    message: str = Field(..., description='Test message to send to the agent')

class TrainingTestResponse(BaseModel):
    response: str = Field(..., description='Agent response')
    response_time_ms: int = Field(..., description='Response time in milliseconds')
    execution_log: List[str] = Field(..., description='Execution log')
    interaction_id: Optional[str] = Field(None, description='ID of the training interaction')
    session_id: Optional[str] = Field(None, description='ID of the training session')
    agent_state: Dict[str, Any] = Field(..., description='Agent state after interaction')
