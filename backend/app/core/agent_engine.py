"""
Agent Engine for Real-time Testing and Execution

This module provides the core agent execution engine that integrates with the
Learning & Training System for real-time testing, data collection, and learning.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.agent import AgentModel
from app.models.training import TrainingSession, TrainingInteraction, TrainingCorrection
from app.core.database import get_db
from app.core.ai_providers import get_ai_provider
from app.core.knowledge import KnowledgeBase
from app.core.content_analysis import analyze_content

logger = logging.getLogger(__name__)


class AgentExecutionContext:
    """
    Context for agent execution that includes training data collection
    """
    
    def __init__(self, agent_id: int, user_id: int, session_id: Optional[str] = None):
        self.agent_id = agent_id
        self.user_id = user_id
        self.session_id = session_id
        self.execution_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.execution_log = []
        self.metrics = {}
        self.training_data = {
            "interactions": [],
            "performance": {},
            "learning_opportunities": []
        }
        
    def log_execution_step(self, step: str, details: Dict[str, Any]):
        """Log an execution step for debugging and training"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "step": step,
            "details": details,
            "execution_time": time.time() - self.start_time
        }
        self.execution_log.append(log_entry)
        
    def capture_training_data(self, interaction_data: Dict[str, Any]):
        """Capture training data from agent execution"""
        self.training_data["interactions"].append(interaction_data)
        
    def identify_learning_opportunities(self, correction_data: Dict[str, Any]):
        """Identify potential learning opportunities from corrections"""
        self.training_data["learning_opportunities"].append(correction_data)
        
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of agent execution"""
        return {
            "execution_id": self.execution_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "duration_ms": int((time.time() - self.start_time) * 1000),
            "steps": len(self.execution_log),
            "training_data_collected": len(self.training_data["interactions"]),
            "learning_opportunities": len(self.training_data["learning_opportunities"])
        }


class AgentEngine:
    """
    Core agent execution engine with training integration
    """
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.active_sessions = {}  # session_id -> AgentExecutionContext
        
    async def initialize(self):
        """Initialize the agent engine"""
        await self.knowledge_base.initialize()
        logger.info("AgentEngine initialized")
        
    async def execute_agent(
        self,
        agent_id: int,
        user_input: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Execute agent with training context and data collection
        """
        
        # Create execution context
        execution_context = AgentExecutionContext(agent_id, context.get("user_id") if context else None, session_id)
        
        try:
            # Load agent configuration
            agent = await self._load_agent(agent_id, db)
            
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            
            execution_context.log_execution_step("agent_loaded", {"agent_name": agent.name})
            
            # Pre-process input
            processed_input = await self._preprocess_input(user_input, agent, execution_context)
            execution_context.log_execution_step("input_processed", {"input": processed_input})
            
            # Generate agent response
            start_time = time.time()
            agent_response = await self._generate_response(processed_input, agent, execution_context)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            execution_context.log_execution_step("response_generated", {
                "response": agent_response,
                "response_time_ms": response_time_ms
            })
            
            # Post-process response
            final_response = await self._postprocess_response(agent_response, agent, execution_context)
            execution_context.log_execution_step("response_postprocessed", {"final_response": final_response})
            
            # Capture training data if in training session
            if session_id:
                await self._capture_training_data(
                    session_id,
                    user_input,
                    final_response,
                    response_time_ms,
                    execution_context,
                    db
                )
            
            # Return execution result
            result = {
                "response": final_response,
                "response_time_ms": response_time_ms,
                "execution_log": execution_context.execution_log,
                "execution_summary": execution_context.get_execution_summary(),
                "agent_state": {
                    "last_execution": datetime.utcnow().isoformat(),
                    "status": "active"
                }
            }
            
            return result
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "execution_log": execution_context.execution_log,
                "execution_summary": execution_context.get_execution_summary()
            }
            logger.error(f"Agent execution failed: {str(e)}")
            raise
        
    async def _load_agent(self, agent_id: int, db: AsyncSession) -> Optional[AgentModel]:
        """Load agent configuration from database"""
        if not db:
            return None
            
        result = await db.execute(select(AgentModel).where(AgentModel.id == agent_id))
        return result.scalar_one_or_none()
        
    async def _preprocess_input(self, user_input: str, agent: AgentModel, context: AgentExecutionContext) -> str:
        """Preprocess user input for agent execution"""
        
        # Analyze content for intent, entities, etc.
        analysis = analyze_content(user_input)
        context.log_execution_step("content_analysis", analysis)
        
        # Apply agent-specific preprocessing
        processed_input = user_input
        
        if agent.system_prompt:
            # Combine system prompt with user input
            processed_input = f"{agent.system_prompt}\n\nUser: {user_input}"
        
        return processed_input
        
    async def _generate_response(self, processed_input: str, agent: AgentModel, context: AgentExecutionContext) -> str:
        """Generate agent response using AI provider"""
        
        # Get AI provider
        ai_provider = get_ai_provider(agent.model_config.get("provider", "openai"))
        
        if not ai_provider:
            raise ValueError(f"AI provider not configured: {agent.model_config.get('provider')}")
        
        # Prepare prompt
        prompt = self._prepare_prompt(processed_input, agent)
        context.log_execution_step("prompt_prepared", {"prompt_length": len(prompt)})
        
        # Generate response using AI provider
        response = await ai_provider.generate_response(
            prompt=prompt,
            model=agent.model_config.get("model", "gpt-3.5-turbo"),
            temperature=agent.model_config.get("temperature", 0.7),
            max_tokens=agent.model_config.get("max_tokens", 150)
        )
        
        context.log_execution_step("ai_response_generated", {
            "response_length": len(response),
            "model": agent.model_config.get("model")
        })
        
        return response
        
    def _prepare_prompt(self, processed_input: str, agent: AgentModel) -> str:
        """Prepare prompt for AI provider"""
        
        # Use agent's user prompt template if available
        if agent.user_prompt_template:
            prompt = agent.user_prompt_template.replace("{{user_input}}", processed_input)
        else:
            prompt = processed_input
        
        return prompt
        
    async def _postprocess_response(self, response: str, agent: AgentModel, context: AgentExecutionContext) -> str:
        """Postprocess agent response"""
        
        # Apply agent-specific postprocessing
        final_response = response
        
        # Add agent personality and style if configured
        if agent.sub_agent_config:
            sub_agent_config = agent.sub_agent_config
            personality = sub_agent_config.get("personality_agent", {})
            
            if personality.get("enabled", False):
                # Apply personality traits (simplified for now)
                final_response = self._apply_personality(response, personality)
        
        return final_response
        
    def _apply_personality(self, response: str, personality_config: Dict[str, Any]) -> str:
        """Apply personality traits to response"""
        # Simplified personality application
        # In a real implementation, this would use more sophisticated NLP
        traits = personality_config.get("personality_traits", {})
        
        # Example: Add more friendliness if trait is high
        if traits.get("friendliness", 0) > 0.7:
            response = f"😊 {response}"
        
        return response
        
    async def _capture_training_data(
        self,
        session_id: str,
        user_input: str,
        agent_response: str,
        response_time_ms: int,
        context: AgentExecutionContext,
        db: AsyncSession
    ):
        """Capture training data during agent execution"""
        
        try:
            # Get or create training session
            result = await db.execute(
                select(TrainingSession).where(TrainingSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                # Create new session if it doesn't exist
                session = TrainingSession(
                    id=session_id,
                    agent_id=context.agent_id,
                    user_id=context.user_id,
                    session_name=f"Training Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                    started_at=datetime.utcnow(),
                    status="active"
                )
                db.add(session)
                await db.commit()
                await db.refresh(session)
            
            # Get next interaction order
            result = await db.execute(
                select(func.max(TrainingInteraction.interaction_order)).
                where(TrainingInteraction.session_id == session_id)
            )
            max_order = result.scalar_one_or_none() or 0
            
            # Create training interaction
            interaction = TrainingInteraction(
                session_id=session_id,
                interaction_order=max_order + 1,
                user_input=user_input,
                agent_response=agent_response,
                response_time_ms=response_time_ms,
                metadata={
                    "execution_log": context.execution_log,
                    "agent_state": context.get_execution_summary(),
                    "context": context.training_data
                }
            )
            
            db.add(interaction)
            await db.commit()
            await db.refresh(interaction)
            
            context.log_execution_step("training_data_captured", {
                "interaction_id": str(interaction.id),
                "session_id": session_id
            })
            
        except Exception as e:
            logger.error(f"Failed to capture training data: {str(e)}")
            context.log_execution_step("training_data_error", {
                "error": str(e)
            })
            
    async def apply_correction(
        self,
        correction_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Apply a training correction to improve agent behavior"""
        
        try:
            # Get correction
            result = await db.execute(
                select(TrainingCorrection).where(TrainingCorrection.id == correction_id)
            )
            correction = result.scalar_one_or_none()
            
            if not correction:
                raise ValueError(f"Correction {correction_id} not found")
            
            # Get associated agent
            result = await db.execute(
                select(TrainingInteraction).where(TrainingInteraction.id == correction.interaction_id)
            )
            interaction = result.scalar_one_or_none()
            
            if not interaction:
                raise ValueError(f"Interaction {correction.interaction_id} not found")
            
            result = await db.execute(
                select(TrainingSession).where(TrainingSession.id == interaction.session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                raise ValueError(f"Session {interaction.session_id} not found")
            
            # Get agent
            result = await db.execute(
                select(AgentModel).where(AgentModel.id == session.agent_id)
            )
            agent = result.scalar_one_or_none()
            
            if not agent:
                raise ValueError(f"Agent {session.agent_id} not found")
            
            # Apply correction based on type
            changes = {}
            
            if correction.correction_type == "response":
                # Update agent's response patterns
                changes = await self._apply_response_correction(agent, correction)
                
            elif correction.correction_type == "behavior":
                # Update agent's behavior configuration
                changes = await self._apply_behavior_correction(agent, correction)
                
            elif correction.correction_type == "knowledge":
                # Update agent's knowledge base
                changes = await self._apply_knowledge_correction(agent, correction)
            
            # Update correction status
            correction.status = "applied"
            correction.applied_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(correction)
            
            return {
                "success": True,
                "correction_id": correction_id,
                "changes_applied": changes,
                "applied_at": correction.applied_at
            }
            
        except Exception as e:
            logger.error(f"Failed to apply correction: {str(e)}")
            raise
            
    async def _apply_response_correction(
        self,
        agent: AgentModel,
        correction: TrainingCorrection
    ) -> Dict[str, Any]:
        """Apply response correction to agent"""
        
        changes = {}
        
        # Update system prompt to include correction
        if agent.system_prompt:
            updated_prompt = f"{agent.system_prompt}\n\nCorrection: {correction.improvement_notes}"
            changes["system_prompt"] = updated_prompt
        else:
            changes["system_prompt"] = f"Correction: {correction.improvement_notes}"
        
        # Apply changes to agent
        for field, value in changes.items():
            setattr(agent, field, value)
        
        return changes
        
    async def _apply_behavior_correction(
        self,
        agent: AgentModel,
        correction: TrainingCorrection
    ) -> Dict[str, Any]:
        """Apply behavior correction to agent"""
        
        changes = {}
        
        # Parse behavior changes from correction
        if correction.improvement_notes:
            # Simple parsing - in real implementation, use proper parsing
            if "temperature" in correction.improvement_notes.lower():
                changes["temperature"] = 0.5  # Example: make more conservative
            
            if "creative" in correction.improvement_notes.lower():
                changes["temperature"] = 0.9  # Example: make more creative
        
        # Update model config
        if not agent.model_config:
            agent.model_config = {}
        
        agent.model_config.update(changes)
        
        return {"model_config": changes}
        
    async def _apply_knowledge_correction(
        self,
        agent: AgentModel,
        correction: TrainingCorrection
    ) -> Dict[str, Any]:
        """Apply knowledge correction to agent"""
        
        changes = {}
        
        # Add correction to knowledge base
        knowledge_entry = {
            "question": correction.original_content,
            "answer": correction.corrected_content,
            "source": "training_correction",
            "confidence": 0.95,
            "tags": ["training", "correction"]
        }
        
        await self.knowledge_base.add_knowledge(agent.id, knowledge_entry)
        
        changes["knowledge_base"] = {
            "added_entries": 1,
            "entry_id": str(uuid.uuid4())
        }
        
        return changes
        
    async def get_training_analytics(
        self,
        agent_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get training analytics for an agent"""
        
        # Get training sessions
        result = await db.execute(
            select(TrainingSession).where(TrainingSession.agent_id == agent_id)
        )
        sessions = result.scalars().all()
        
        # Get training interactions
        result = await db.execute(
            select(TrainingInteraction).
            join(TrainingSession).
            where(TrainingSession.agent_id == agent_id)
        )
        interactions = result.scalars().all()
        
        # Get corrections
        result = await db.execute(
            select(TrainingCorrection).
            join(TrainingInteraction).
            join(TrainingSession).
            where(TrainingSession.agent_id == agent_id)
        )
        corrections = result.scalars().all()
        
        # Calculate metrics
        total_sessions = len(sessions)
        total_interactions = len(interactions)
        total_corrections = len(corrections)
        
        avg_response_time = 0
        if total_interactions > 0:
            avg_response_time = sum(i.response_time_ms for i in interactions if i.response_time_ms) / total_interactions
        
        applied_corrections = sum(1 for c in corrections if c.status == "applied")
        correction_rate = applied_corrections / max(total_interactions, 1)
        
        return {
            "agent_id": agent_id,
            "total_sessions": total_sessions,
            "total_interactions": total_interactions,
            "total_corrections": total_corrections,
            "applied_corrections": applied_corrections,
            "avg_response_time_ms": avg_response_time,
            "correction_rate": correction_rate,
            "performance_trends": {
                "response_time": self._calculate_trend([i.response_time_ms for i in interactions if i.response_time_ms]),
                "correction_rate": self._calculate_trend([correction_rate])
            }
        }
        
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from a series of values"""
        if len(values) < 2:
            return "stable"
        
        # Simple trend calculation
        if values[-1] < values[0]:
            return "improving"
        elif values[-1] > values[0]:
            return "declining"
        else:
            return "stable"


# Global AgentEngine instance
_agent_engine: Optional[AgentEngine] = None


async def initialize_agent_engine():
    """Initialize the global AgentEngine"""
    global _agent_engine
    
    if _agent_engine is None:
        _agent_engine = AgentEngine()
        await _agent_engine.initialize()
        logger.info("AgentEngine initialized successfully")
    
    return _agent_engine


async def cleanup_agent_engine():
    """Cleanup AgentEngine resources"""
    global _agent_engine
    
    if _agent_engine:
        # Cleanup resources
        await _agent_engine.knowledge_base.cleanup()
        logger.info("AgentEngine cleaned up")
        _agent_engine = None


async def get_agent_engine() -> AgentEngine:
    """Get or create global AgentEngine instance"""
    global _agent_engine
    
    if _agent_engine is None:
        _agent_engine = await initialize_agent_engine()
    
    return _agent_engine