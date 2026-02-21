"""
FUZZY Tools Engine

Business logic for FUZZY studio manipulation tools.
Provides safe, auditable operations for agent management, configuration, and publishing.
"""
import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.agent import AgentModel, Action, AgentStatus
from app.models.knowledge import KnowledgeFile
from app.models.communication_channel import CommunicationChannel
from app.models.integration import Integration
from app.models.marketplace import MarketplaceListing
from app.models.fuzzy_session import (
    FuzzySession, FuzzyAction, FuzzyRateLimit,
    FuzzyActionType, FuzzyActionStatus
)
from app.schemas.fuzzy_tools import (
    CreateAgentRequest, UpdateAgentConfigRequest, DeleteAgentRequest,
    AddToolToAgentRequest, RemoveToolFromAgentRequest,
    UpdateAgentInstructionsRequest, AddKnowledgeFileRequest,
    ConfigureCommunicationChannelRequest, PublishAgentRequest,
    PublishToMarketplaceRequest, UnpublishAgentRequest,
    FuzzyToolResponse, AgentDetailsResponse, ToolListResponse,
    IntegrationListResponse, AgentListResponse, RateLimitStatus
)

logger = logging.getLogger(__name__)


class FuzzyToolsEngine:
    """
    Core engine for FUZZY studio manipulation tools.
    
    Provides methods for:
    - Agent management (create, update, delete)
    - Studio configuration (tools, knowledge, channels)
    - Publishing operations
    - Query operations
    - Rate limiting and audit trail
    """
    
    def __init__(self, db: Session, user_id: int, session_token: Optional[str] = None):
        """
        Initialize the FUZZY tools engine.
        
        Args:
            db: Database session
            user_id: ID of the user performing operations
            session_token: Optional session token for continuing a session
        """
        self.db = db
        self.user_id = user_id
        self.session = self._get_or_create_session(session_token)
        logger.info(f"FuzzyToolsEngine initialized for user {user_id}, session {self.session.session_token}")
    
    def _get_or_create_session(self, session_token: Optional[str]) -> FuzzySession:
        """Get existing session or create a new one"""
        if session_token:
            session = self.db.query(FuzzySession).filter(
                and_(
                    FuzzySession.session_token == session_token,
                    FuzzySession.user_id == self.user_id,
                    FuzzySession.is_active == True
                )
            ).first()
            if session:
                session.last_activity_at = datetime.utcnow()
                self.db.commit()
                return session
        
        # Create new session
        session = FuzzySession(
            user_id=self.user_id,
            session_token=str(uuid.uuid4()),
            is_active=True,
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
            context={}
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def _check_rate_limit(self) -> bool:
        """Check if user has exceeded rate limits"""
        now = datetime.utcnow()
        rate_limit = self.db.query(FuzzyRateLimit).filter(
            FuzzyRateLimit.user_id == self.user_id
        ).first()
        
        if not rate_limit:
            # Create new rate limit record
            rate_limit = FuzzyRateLimit(
                user_id=self.user_id,
                actions_count_hourly=0,
                actions_count_daily=0,
                hourly_reset_at=now + timedelta(hours=1),
                daily_reset_at=now + timedelta(days=1)
            )
            self.db.add(rate_limit)
            self.db.commit()
            return True
        
        # Reset counters if needed
        if now >= rate_limit.hourly_reset_at:
            rate_limit.actions_count_hourly = 0
            rate_limit.hourly_reset_at = now + timedelta(hours=1)
        
        if now >= rate_limit.daily_reset_at:
            rate_limit.actions_count_daily = 0
            rate_limit.daily_reset_at = now + timedelta(days=1)
        
        # Check limits
        if rate_limit.actions_count_hourly >= rate_limit.hourly_limit:
            logger.warning(f"User {self.user_id} exceeded hourly rate limit")
            return False
        
        if rate_limit.actions_count_daily >= rate_limit.daily_limit:
            logger.warning(f"User {self.user_id} exceeded daily rate limit")
            return False
        
        # Increment counters
        rate_limit.actions_count_hourly += 1
        rate_limit.actions_count_daily += 1
        self.db.commit()
        
        return True
    
    def _log_action(
        self,
        action_type: FuzzyActionType,
        action_name: str,
        parameters: Dict[str, Any],
        status: FuzzyActionStatus,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        affected_resource_type: Optional[str] = None,
        affected_resource_id: Optional[int] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        can_rollback: bool = False
    ) -> FuzzyAction:
        """Log an action to the audit trail"""
        action = FuzzyAction(
            session_id=self.session.id,
            user_id=self.user_id,
            action_type=action_type,
            action_name=action_name,
            description=f"FUZZY performed {action_name}",
            parameters=parameters,
            result=result,
            error_message=error_message,
            status=status,
            execution_time_ms=execution_time_ms,
            affected_resource_type=affected_resource_type,
            affected_resource_id=affected_resource_id,
            previous_state=previous_state,
            new_state=new_state,
            can_rollback=can_rollback
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        
        logger.info(
            f"Action logged: {action_type.value} - {action_name} "
            f"(status: {status.value}, user: {self.user_id})"
        )
        
        return action
    
    def _verify_agent_ownership(self, agent_id: int) -> Optional[AgentModel]:
        """Verify that the user owns the specified agent"""
        agent = self.db.query(AgentModel).filter(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == self.user_id
            )
        ).first()
        
        if not agent:
            logger.warning(f"User {self.user_id} attempted to access agent {agent_id} without ownership")
        
        return agent
    
    # ============== Agent Management Tools ==============
    
    def create_agent(self, request: CreateAgentRequest) -> FuzzyToolResponse:
        """Create a new agent"""
        start_time = time.time()
        
        # Check rate limit
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        try:
            # Create agent
            agent = AgentModel(
                name=request.name,
                description=request.description,
                system_prompt=request.system_prompt,
                model_config=request.model_config_data or {},
                tags=request.tags or [],
                status=AgentStatus.DRAFT,
                owner_id=self.user_id,
                usage_count=0,
                success_rate=0.0,
                avg_response_time=0.0
            )
            
            self.db.add(agent)
            self.db.commit()
            self.db.refresh(agent)
            
            execution_time = (time.time() - start_time) * 1000
            
            # Log action
            action = self._log_action(
                action_type=FuzzyActionType.CREATE_AGENT,
                action_name="create_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.COMPLETED,
                result={"agent_id": agent.id, "agent_name": agent.name},
                execution_time_ms=execution_time,
                affected_resource_type="agent",
                affected_resource_id=agent.id,
                new_state={"name": agent.name, "status": agent.status.value},
                can_rollback=True
            )
            
            logger.info(f"Agent created: {agent.id} - {agent.name} by user {self.user_id}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Agent '{agent.name}' created successfully",
                data={
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "status": agent.status.value
                },
                action_id=action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error creating agent: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.CREATE_AGENT,
                action_name="create_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to create agent: {str(e)}",
                data=None
            )
    
    def update_agent_config(self, request: UpdateAgentConfigRequest) -> FuzzyToolResponse:
        """Update agent configuration"""
        start_time = time.time()
        
        # Check rate limit
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        # Verify ownership
        agent = self._verify_agent_ownership(request.agent_id)
        if not agent:
            return FuzzyToolResponse(
                success=False,
                message=f"Agent {request.agent_id} not found or access denied",
                data=None
            )
        
        try:
            # Store previous state
            previous_state = {
                "name": agent.name,
                "description": agent.description,
                "system_prompt": agent.system_prompt,
                "model_config": agent.model_config,
                "tags": agent.tags
            }
            
            # Update fields
            if request.name is not None:
                agent.name = request.name
            if request.description is not None:
                agent.description = request.description
            if request.system_prompt is not None:
                agent.system_prompt = request.system_prompt
            if request.model_config_data is not None:
                agent.model_config = request.model_config_data
            if request.tags is not None:
                agent.tags = request.tags
            
            self.db.commit()
            self.db.refresh(agent)
            
            execution_time = (time.time() - start_time) * 1000
            
            # Log action
            action = self._log_action(
                action_type=FuzzyActionType.UPDATE_AGENT,
                action_name="update_agent_config",
                parameters=request.dict(),
                status=FuzzyActionStatus.COMPLETED,
                result={"agent_id": agent.id, "updated_fields": list(request.dict(exclude_unset=True).keys())},
                execution_time_ms=execution_time,
                affected_resource_type="agent",
                affected_resource_id=agent.id,
                previous_state=previous_state,
                new_state={
                    "name": agent.name,
                    "description": agent.description,
                    "system_prompt": agent.system_prompt,
                    "model_config": agent.model_config,
                    "tags": agent.tags
                },
                can_rollback=True
            )
            
            logger.info(f"Agent updated: {agent.id} by user {self.user_id}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Agent '{agent.name}' updated successfully",
                data={"agent_id": agent.id, "agent_name": agent.name},
                action_id=action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error updating agent: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.UPDATE_AGENT,
                action_name="update_agent_config",
                parameters=request.dict(),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time,
                affected_resource_type="agent",
                affected_resource_id=request.agent_id
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to update agent: {str(e)}",
                data=None
            )
    
    def delete_agent(self, request: DeleteAgentRequest) -> FuzzyToolResponse:
        """Delete an agent"""
        start_time = time.time()
        
        # Check rate limit
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        # Verify ownership
        agent = self._verify_agent_ownership(request.agent_id)
        if not agent:
            return FuzzyToolResponse(
                success=False,
                message=f"Agent {request.agent_id} not found or access denied",
                data=None
            )
        
        try:
            # Store state for potential rollback
            previous_state = {
                "name": agent.name,
                "description": agent.description,
                "status": agent.status.value,
                "system_prompt": agent.system_prompt,
                "model_config": agent.model_config
            }
            
            agent_id = agent.id
            agent_name = agent.name
            
            # Delete agent (cascade will handle related records)
            self.db.delete(agent)
            self.db.commit()
            
            execution_time = (time.time() - start_time) * 1000
            
            # Log action
            action = self._log_action(
                action_type=FuzzyActionType.DELETE_AGENT,
                action_name="delete_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.COMPLETED,
                result={"agent_id": agent_id, "agent_name": agent_name},
                execution_time_ms=execution_time,
                affected_resource_type="agent",
                affected_resource_id=agent_id,
                previous_state=previous_state,
                can_rollback=False  # Deletion is not easily reversible
            )
            
            logger.info(f"Agent deleted: {agent_id} by user {self.user_id}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Agent '{agent_name}' deleted successfully",
                data={"agent_id": agent_id},
                action_id=action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error deleting agent: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.DELETE_AGENT,
                action_name="delete_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time,
                affected_resource_type="agent",
                affected_resource_id=request.agent_id
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to delete agent: {str(e)}",
                data=None
            )
    
    def list_user_agents(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> AgentListResponse:
        """List user's agents"""
        query = self.db.query(AgentModel).filter(AgentModel.owner_id == self.user_id)
        
        if status:
            try:
                status_enum = AgentStatus(status)
                query = query.filter(AgentModel.status == status_enum)
            except ValueError:
                pass
        
        total = query.count()
        agents = query.offset(offset).limit(limit).all()
        
        agents_data = [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "status": agent.status.value,
                "tags": agent.tags,
                "created_at": agent.created_at.isoformat(),
                "updated_at": agent.updated_at.isoformat()
            }
            for agent in agents
        ]
        
        return AgentListResponse(
            agents=agents_data,
            total=total,
            limit=limit,
            offset=offset
        )
    
    # ============== Studio Configuration Tools ==============
    
    def add_tool_to_agent(self, request: AddToolToAgentRequest) -> FuzzyToolResponse:
        """Add a tool to an agent"""
        start_time = time.time()
        
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        agent = self._verify_agent_ownership(request.agent_id)
        if not agent:
            return FuzzyToolResponse(
                success=False,
                message=f"Agent {request.agent_id} not found or access denied",
                data=None
            )
        
        try:
            # Create action/tool
            action = Action(
                agent_id=agent.id,
                name=request.tool_name,
                action_type=request.tool_type,
                config=request.tool_config or {},
                parameters=request.parameters or {},
                status="active"
            )
            
            self.db.add(action)
            self.db.commit()
            self.db.refresh(action)
            
            execution_time = (time.time() - start_time) * 1000
            
            fuzzy_action = self._log_action(
                action_type=FuzzyActionType.ADD_TOOL,
                action_name="add_tool_to_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.COMPLETED,
                result={"tool_id": action.id, "tool_name": action.name},
                execution_time_ms=execution_time,
                affected_resource_type="tool",
                affected_resource_id=action.id,
                can_rollback=True
            )
            
            logger.info(f"Tool added to agent {agent.id}: {action.name}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Tool '{action.name}' added to agent '{agent.name}'",
                data={"tool_id": action.id, "tool_name": action.name},
                action_id=fuzzy_action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error adding tool to agent: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.ADD_TOOL,
                action_name="add_tool_to_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to add tool: {str(e)}",
                data=None
            )
    
    def remove_tool_from_agent(self, request: RemoveToolFromAgentRequest) -> FuzzyToolResponse:
        """Remove a tool from an agent"""
        start_time = time.time()
        
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        agent = self._verify_agent_ownership(request.agent_id)
        if not agent:
            return FuzzyToolResponse(
                success=False,
                message=f"Agent {request.agent_id} not found or access denied",
                data=None
            )
        
        try:
            # Find tool
            tool = self.db.query(Action).filter(
                and_(
                    Action.id == request.tool_id,
                    Action.agent_id == agent.id
                )
            ).first()
            
            if not tool:
                return FuzzyToolResponse(
                    success=False,
                    message=f"Tool {request.tool_id} not found for this agent",
                    data=None
                )
            
            tool_name = tool.name
            previous_state = {
                "name": tool.name,
                "action_type": tool.action_type,
                "config": tool.config
            }
            
            self.db.delete(tool)
            self.db.commit()
            
            execution_time = (time.time() - start_time) * 1000
            
            fuzzy_action = self._log_action(
                action_type=FuzzyActionType.REMOVE_TOOL,
                action_name="remove_tool_from_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.COMPLETED,
                result={"tool_id": request.tool_id, "tool_name": tool_name},
                execution_time_ms=execution_time,
                affected_resource_type="tool",
                affected_resource_id=request.tool_id,
                previous_state=previous_state,
                can_rollback=False
            )
            
            logger.info(f"Tool removed from agent {agent.id}: {tool_name}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Tool '{tool_name}' removed from agent '{agent.name}'",
                data={"tool_id": request.tool_id},
                action_id=fuzzy_action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error removing tool from agent: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.REMOVE_TOOL,
                action_name="remove_tool_from_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to remove tool: {str(e)}",
                data=None
            )
    
    def update_agent_instructions(self, request: UpdateAgentInstructionsRequest) -> FuzzyToolResponse:
        """Update agent instructions/system prompt"""
        start_time = time.time()
        
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        agent = self._verify_agent_ownership(request.agent_id)
        if not agent:
            return FuzzyToolResponse(
                success=False,
                message=f"Agent {request.agent_id} not found or access denied",
                data=None
            )
        
        try:
            previous_state = {
                "system_prompt": agent.system_prompt,
                "user_prompt_template": agent.user_prompt_template
            }
            
            agent.system_prompt = request.system_prompt
            if request.user_prompt_template is not None:
                agent.user_prompt_template = request.user_prompt_template
            
            self.db.commit()
            
            execution_time = (time.time() - start_time) * 1000
            
            fuzzy_action = self._log_action(
                action_type=FuzzyActionType.UPDATE_INSTRUCTIONS,
                action_name="update_agent_instructions",
                parameters=request.dict(),
                status=FuzzyActionStatus.COMPLETED,
                result={"agent_id": agent.id},
                execution_time_ms=execution_time,
                affected_resource_type="agent",
                affected_resource_id=agent.id,
                previous_state=previous_state,
                new_state={
                    "system_prompt": agent.system_prompt,
                    "user_prompt_template": agent.user_prompt_template
                },
                can_rollback=True
            )
            
            logger.info(f"Instructions updated for agent {agent.id}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Instructions updated for agent '{agent.name}'",
                data={"agent_id": agent.id},
                action_id=fuzzy_action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error updating agent instructions: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.UPDATE_INSTRUCTIONS,
                action_name="update_agent_instructions",
                parameters=request.dict(),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to update instructions: {str(e)}",
                data=None
            )
    
    def add_knowledge_file(self, request: AddKnowledgeFileRequest) -> FuzzyToolResponse:
        """Add knowledge file to agent"""
        start_time = time.time()
        
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        agent = self._verify_agent_ownership(request.agent_id)
        if not agent:
            return FuzzyToolResponse(
                success=False,
                message=f"Agent {request.agent_id} not found or access denied",
                data=None
            )
        
        try:
            # Create knowledge file record
            knowledge_file = KnowledgeFile(
                agent_id=agent.id,
                filename=request.file_name,
                file_type=request.file_type,
                file_url=request.file_url,
                metadata=request.metadata or {},
                status="active"
            )
            
            self.db.add(knowledge_file)
            self.db.commit()
            self.db.refresh(knowledge_file)
            
            execution_time = (time.time() - start_time) * 1000
            
            fuzzy_action = self._log_action(
                action_type=FuzzyActionType.ADD_KNOWLEDGE,
                action_name="add_knowledge_file",
                parameters=request.dict(exclude={"file_content"}),  # Don't log file content
                status=FuzzyActionStatus.COMPLETED,
                result={"knowledge_file_id": knowledge_file.id, "filename": knowledge_file.filename},
                execution_time_ms=execution_time,
                affected_resource_type="knowledge_file",
                affected_resource_id=knowledge_file.id,
                can_rollback=True
            )
            
            logger.info(f"Knowledge file added to agent {agent.id}: {knowledge_file.filename}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Knowledge file '{knowledge_file.filename}' added to agent '{agent.name}'",
                data={"knowledge_file_id": knowledge_file.id, "filename": knowledge_file.filename},
                action_id=fuzzy_action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error adding knowledge file: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.ADD_KNOWLEDGE,
                action_name="add_knowledge_file",
                parameters=request.dict(exclude={"file_content"}),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to add knowledge file: {str(e)}",
                data=None
            )
    
    def configure_communication_channel(self, request: ConfigureCommunicationChannelRequest) -> FuzzyToolResponse:
        """Configure communication channel for agent"""
        start_time = time.time()
        
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        agent = self._verify_agent_ownership(request.agent_id)
        if not agent:
            return FuzzyToolResponse(
                success=False,
                message=f"Agent {request.agent_id} not found or access denied",
                data=None
            )
        
        try:
            # Create or update communication channel
            channel = CommunicationChannel(
                agent_id=agent.id,
                channel_type=request.channel_type,
                config=request.channel_config,
                is_active=request.is_active
            )
            
            self.db.add(channel)
            self.db.commit()
            self.db.refresh(channel)
            
            execution_time = (time.time() - start_time) * 1000
            
            fuzzy_action = self._log_action(
                action_type=FuzzyActionType.CONFIGURE_CHANNEL,
                action_name="configure_communication_channel",
                parameters=request.dict(),
                status=FuzzyActionStatus.COMPLETED,
                result={"channel_id": channel.id, "channel_type": channel.channel_type},
                execution_time_ms=execution_time,
                affected_resource_type="communication_channel",
                affected_resource_id=channel.id,
                can_rollback=True
            )
            
            logger.info(f"Communication channel configured for agent {agent.id}: {channel.channel_type}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Communication channel '{channel.channel_type}' configured for agent '{agent.name}'",
                data={"channel_id": channel.id, "channel_type": channel.channel_type},
                action_id=fuzzy_action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error configuring communication channel: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.CONFIGURE_CHANNEL,
                action_name="configure_communication_channel",
                parameters=request.dict(),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to configure communication channel: {str(e)}",
                data=None
            )
    
    # ============== Publishing Tools ==============
    
    def publish_agent(self, request: PublishAgentRequest) -> FuzzyToolResponse:
        """Publish agent to communication channels"""
        start_time = time.time()
        
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        agent = self._verify_agent_ownership(request.agent_id)
        if not agent:
            return FuzzyToolResponse(
                success=False,
                message=f"Agent {request.agent_id} not found or access denied",
                data=None
            )
        
        try:
            # Update agent status to active
            previous_status = agent.status
            agent.status = AgentStatus.ACTIVE
            self.db.commit()
            
            execution_time = (time.time() - start_time) * 1000
            
            fuzzy_action = self._log_action(
                action_type=FuzzyActionType.PUBLISH_AGENT,
                action_name="publish_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.COMPLETED,
                result={"agent_id": agent.id, "channels": request.channels},
                execution_time_ms=execution_time,
                affected_resource_type="agent",
                affected_resource_id=agent.id,
                previous_state={"status": previous_status.value},
                new_state={"status": agent.status.value},
                can_rollback=True
            )
            
            logger.info(f"Agent published: {agent.id} to channels {request.channels}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Agent '{agent.name}' published successfully",
                data={"agent_id": agent.id, "channels": request.channels},
                action_id=fuzzy_action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error publishing agent: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.PUBLISH_AGENT,
                action_name="publish_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to publish agent: {str(e)}",
                data=None
            )
    
    def unpublish_agent(self, request: UnpublishAgentRequest) -> FuzzyToolResponse:
        """Unpublish agent from channels"""
        start_time = time.time()
        
        if not self._check_rate_limit():
            return FuzzyToolResponse(
                success=False,
                message="Rate limit exceeded. Please try again later.",
                data=None
            )
        
        agent = self._verify_agent_ownership(request.agent_id)
        if not agent:
            return FuzzyToolResponse(
                success=False,
                message=f"Agent {request.agent_id} not found or access denied",
                data=None
            )
        
        try:
            previous_status = agent.status
            agent.status = AgentStatus.INACTIVE
            self.db.commit()
            
            execution_time = (time.time() - start_time) * 1000
            
            fuzzy_action = self._log_action(
                action_type=FuzzyActionType.UNPUBLISH_AGENT,
                action_name="unpublish_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.COMPLETED,
                result={"agent_id": agent.id},
                execution_time_ms=execution_time,
                affected_resource_type="agent",
                affected_resource_id=agent.id,
                previous_state={"status": previous_status.value},
                new_state={"status": agent.status.value},
                can_rollback=True
            )
            
            logger.info(f"Agent unpublished: {agent.id}")
            
            return FuzzyToolResponse(
                success=True,
                message=f"Agent '{agent.name}' unpublished successfully",
                data={"agent_id": agent.id},
                action_id=fuzzy_action.id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error unpublishing agent: {e}")
            
            self._log_action(
                action_type=FuzzyActionType.UNPUBLISH_AGENT,
                action_name="unpublish_agent",
                parameters=request.dict(),
                status=FuzzyActionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            return FuzzyToolResponse(
                success=False,
                message=f"Failed to unpublish agent: {str(e)}",
                data=None
            )
    
    # ============== Query Tools ==============
    
    def get_agent_details(self, agent_id: int) -> Optional[AgentDetailsResponse]:
        """Get detailed information about an agent"""
        agent = self._verify_agent_ownership(agent_id)
        if not agent:
            return None
        
        # Get related data
        tools = self.db.query(Action).filter(Action.agent_id == agent.id).all()
        knowledge_files = self.db.query(KnowledgeFile).filter(KnowledgeFile.agent_id == agent.id).all()
        channels = self.db.query(CommunicationChannel).filter(CommunicationChannel.agent_id == agent.id).all()
        
        return AgentDetailsResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            status=agent.status.value,
            system_prompt=agent.system_prompt,
            model_config=agent.model_config,
            tags=agent.tags,
            tools=[
                {
                    "id": tool.id,
                    "name": tool.name,
                    "type": tool.action_type,
                    "config": tool.config
                }
                for tool in tools
            ],
            knowledge_files=[
                {
                    "id": kf.id,
                    "filename": kf.filename,
                    "file_type": kf.file_type
                }
                for kf in knowledge_files
            ],
            communication_channels=[
                {
                    "id": ch.id,
                    "type": ch.channel_type,
                    "is_active": ch.is_active
                }
                for ch in channels
            ],
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )
    
    def get_available_tools(self, tool_type: Optional[str] = None) -> ToolListResponse:
        """Get list of available tools"""
        # This would typically query a tools catalog
        # For now, return a basic list
        tools = [
            {"name": "web_scraping", "type": "web_scraping", "description": "Scrape web pages"},
            {"name": "api_call", "type": "api_call", "description": "Make API calls"},
            {"name": "database_query", "type": "database_query", "description": "Query databases"},
            {"name": "file_processing", "type": "file_processing", "description": "Process files"},
            {"name": "email_sender", "type": "email", "description": "Send emails"},
        ]
        
        if tool_type:
            tools = [t for t in tools if t["type"] == tool_type]
        
        return ToolListResponse(tools=tools, total=len(tools))
    
    def get_available_integrations(self, integration_type: Optional[str] = None) -> IntegrationListResponse:
        """Get list of available integrations"""
        # Query available integrations
        query = self.db.query(Integration)
        
        if integration_type:
            query = query.filter(Integration.integration_type == integration_type)
        
        integrations = query.all()
        
        integrations_data = [
            {
                "id": integration.id,
                "name": integration.name,
                "type": integration.integration_type,
                "description": integration.description
            }
            for integration in integrations
        ]
        
        return IntegrationListResponse(integrations=integrations_data, total=len(integrations_data))
    
    def get_rate_limit_status(self) -> RateLimitStatus:
        """Get current rate limit status for user"""
        rate_limit = self.db.query(FuzzyRateLimit).filter(
            FuzzyRateLimit.user_id == self.user_id
        ).first()
        
        if not rate_limit:
            now = datetime.utcnow()
            return RateLimitStatus(
                user_id=self.user_id,
                actions_count_hourly=0,
                hourly_limit=100,
                actions_count_daily=0,
                daily_limit=500,
                hourly_remaining=100,
                daily_remaining=500,
                hourly_reset_at=now + timedelta(hours=1),
                daily_reset_at=now + timedelta(days=1)
            )
        
        return RateLimitStatus(
            user_id=self.user_id,
            actions_count_hourly=rate_limit.actions_count_hourly,
            hourly_limit=rate_limit.hourly_limit,
            actions_count_daily=rate_limit.actions_count_daily,
            daily_limit=rate_limit.daily_limit,
            hourly_remaining=max(0, rate_limit.hourly_limit - rate_limit.actions_count_hourly),
            daily_remaining=max(0, rate_limit.daily_limit - rate_limit.actions_count_daily),
            hourly_reset_at=rate_limit.hourly_reset_at,
            daily_reset_at=rate_limit.daily_reset_at
        )
