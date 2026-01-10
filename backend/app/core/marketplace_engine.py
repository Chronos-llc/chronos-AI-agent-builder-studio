"""
Marketplace Engine

Core functionality for marketplace operations including agent copying, installation, and management.
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

from app.models.agent import AgentModel
from app.models.marketplace import MarketplaceListing, MarketplaceInstallation
from app.models.knowledge import KnowledgeFile
from app.models.integration import Integration, IntegrationConfig
from app.models.hook import Hook
from app.models.communication_channel import CommunicationChannel
from app.models.agent_table import AgentTable
from app.models.agent_memory import AgentMemory
from app.models.voice import VoiceConfiguration
from app.core.database import get_db
from fastapi import Depends

logger = logging.getLogger(__name__)


class MarketplaceEngine:
    """Core marketplace operations engine"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def copy_agent_from_marketplace(
        self,
        listing_id: int,
        user_id: int,
        custom_name: Optional[str] = None,
        preserve_original_reference: bool = True
    ) -> AgentModel:
        """
        Copy an agent from marketplace listing to user's account
        
        Args:
            listing_id: ID of the marketplace listing
            user_id: ID of the user copying the agent
            custom_name: Optional custom name for the copied agent
            preserve_original_reference: Whether to preserve reference to original agent
            
        Returns:
            The newly created agent copy
            
        Raises:
            Exception: If listing not found or agent copy fails
        """
        try:
            logger.info(f"Starting agent copy process for listing {listing_id} by user {user_id}")
            
            # Get the marketplace listing with the original agent
            result = await self.db.execute(
                select(MarketplaceListing).where(MarketplaceListing.id == listing_id).options(
                    joinedload(MarketplaceListing.agent)
                )
            )
            listing = result.scalar_one_or_none()
            
            if not listing:
                logger.error(f"Marketplace listing {listing_id} not found")
                raise Exception("Marketplace listing not found")
            
            if not listing.agent:
                logger.error(f"Original agent not found for listing {listing_id}")
                raise Exception("Original agent not found")
            
            original_agent = listing.agent
            
            logger.info(f"Found original agent {original_agent.id} for listing {listing_id}")
            
            # Create the base agent copy
            agent_copy = await self._create_agent_copy(original_agent, user_id, custom_name)
            
            # Copy related entities
            await self._copy_agent_related_entities(original_agent, agent_copy)
            
            # Add marketplace metadata to track the copy
            if preserve_original_reference:
                await self._add_marketplace_metadata(agent_copy, listing, original_agent)
            
            # Create installation record
            installation = MarketplaceInstallation(
                listing_id=listing_id,
                user_id=user_id,
                agent_id=agent_copy.id
            )
            self.db.add(installation)
            
            # Update listing statistics
            listing.install_count += 1
            
            await self.db.commit()
            await self.db.refresh(agent_copy)
            
            logger.info(f"Successfully copied agent {original_agent.id} to user {user_id} as agent {agent_copy.id}")
            
            return agent_copy
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to copy agent from marketplace: {str(e)}", exc_info=True)
            raise Exception(f"Failed to copy agent: {str(e)}")
    
    async def _create_agent_copy(
        self,
        original_agent: AgentModel,
        user_id: int,
        custom_name: Optional[str] = None
    ) -> AgentModel:
        """Create a copy of the base agent"""
        try:
            logger.debug(f"Creating agent copy from original agent {original_agent.id}")
            
            # Generate copy name if not provided
            if custom_name:
                name = custom_name
            else:
                name = f"{original_agent.name} (Copy)"
            
            # Create the agent copy
            agent_copy = AgentModel(
                name=name,
                description=original_agent.description,
                owner_id=user_id,
                status=original_agent.status,
                model_config=original_agent.model_config.copy() if original_agent.model_config else None,
                system_prompt=original_agent.system_prompt,
                user_prompt_template=original_agent.user_prompt_template,
                sub_agent_config=original_agent.sub_agent_config.copy() if original_agent.sub_agent_config else None,
                tags=original_agent.tags.copy() if original_agent.tags else None,
                metadata=self._prepare_copy_metadata(original_agent.metadata),
                usage_count=0,  # Reset usage statistics
                success_rate=0.0,
                avg_response_time=0.0,
                version=original_agent.version,
                icon=original_agent.icon,
                color=original_agent.color,
                preview_image=original_agent.preview_image
            )
            
            self.db.add(agent_copy)
            await self.db.flush()  # Get the ID for related entities
            
            logger.debug(f"Created agent copy with ID {agent_copy.id}")
            
            return agent_copy
            
        except Exception as e:
            logger.error(f"Failed to create agent copy: {str(e)}", exc_info=True)
            raise Exception(f"Failed to create agent copy: {str(e)}")
    
    async def _copy_agent_related_entities(
        self,
        original_agent: AgentModel,
        agent_copy: AgentModel
    ) -> None:
        """Copy all related entities (knowledge, integrations, hooks, etc.)"""
        try:
            logger.debug(f"Starting to copy related entities for agent {original_agent.id}")
            
            # Copy knowledge files
            await self._copy_knowledge_files(original_agent, agent_copy)
            
            # Copy integrations and configs
            await self._copy_integrations(original_agent, agent_copy)
            
            # Copy hooks
            await self._copy_hooks(original_agent, agent_copy)
            
            # Copy communication channels
            await self._copy_communication_channels(original_agent, agent_copy)
            
            # Copy agent tables
            await self._copy_agent_tables(original_agent, agent_copy)
            
            # Copy agent memories
            await self._copy_agent_memories(original_agent, agent_copy)
            
            # Copy voice configuration
            await self._copy_voice_configuration(original_agent, agent_copy)
            
            logger.debug(f"Successfully copied all related entities for agent {agent_copy.id}")
            
        except Exception as e:
            logger.error(f"Failed to copy related entities: {str(e)}", exc_info=True)
            raise Exception(f"Failed to copy related entities: {str(e)}")
    
    async def _copy_knowledge_files(self, original_agent: AgentModel, agent_copy: AgentModel) -> None:
        """Copy knowledge files"""
        try:
            logger.debug(f"Copying knowledge files for agent {original_agent.id}")
            
            result = await self.db.execute(
                select(KnowledgeFile).where(KnowledgeFile.agent_id == original_agent.id)
            )
            knowledge_files = result.scalars().all()
            
            for knowledge_file in knowledge_files:
                # For knowledge files, we copy the metadata but not the actual file
                # The file would need to be copied separately in a real implementation
                knowledge_copy = KnowledgeFile(
                    original_filename=knowledge_file.original_filename,
                    stored_filename=f"copy_{knowledge_file.stored_filename}",  # Unique filename for copy
                    file_path=knowledge_file.file_path,  # This would need to be updated if files are actually copied
                    file_type=knowledge_file.file_type,
                    file_size=knowledge_file.file_size,
                    mime_type=knowledge_file.mime_type,
                    content_text=knowledge_file.content_text,
                    content_summary=knowledge_file.content_summary,
                    content_keywords=knowledge_file.content_keywords.copy() if knowledge_file.content_keywords else None,
                    processing_status=knowledge_file.processing_status,
                    metadata=knowledge_file.metadata.copy() if knowledge_file.metadata else None,
                    tags=knowledge_file.tags.copy() if knowledge_file.tags else None,
                    agent_id=agent_copy.id
                )
                self.db.add(knowledge_copy)
            
            await self.db.flush()
            logger.debug(f"Copied {len(knowledge_files)} knowledge files")
            
        except Exception as e:
            logger.error(f"Failed to copy knowledge files: {str(e)}", exc_info=True)
            raise
    
    async def _copy_integrations(self, original_agent: AgentModel, agent_copy: AgentModel) -> None:
        """Copy integrations and integration configs"""
        try:
            logger.debug(f"Copying integrations for agent {original_agent.id}")
            
            # Copy integrations
            result = await self.db.execute(
                select(Integration).where(Integration.agent_id == original_agent.id)
            )
            integrations = result.scalars().all()
            
            for integration in integrations:
                integration_copy = Integration(
                    name=integration.name,
                    description=integration.description,
                    integration_type=integration.integration_type,
                    category=integration.category,
                    icon=integration.icon,
                    documentation_url=integration.documentation_url,
                    version=integration.version,
                    is_public=integration.is_public,
                    config_schema=integration.config_schema.copy() if integration.config_schema else None,
                    credentials_schema=integration.credentials_schema.copy() if integration.credentials_schema else None,
                    supported_features=integration.supported_features.copy() if integration.supported_features else None,
                    last_sync=integration.last_sync,
                    sync_status=integration.sync_status,
                    download_count=integration.download_count,
                    rating=integration.rating,
                    review_count=integration.review_count,
                    author_id=integration.author_id,
                    agent_id=agent_copy.id
                )
                self.db.add(integration_copy)
            
            # Copy integration configs
            result = await self.db.execute(
                select(IntegrationConfig).where(IntegrationConfig.agent_id == original_agent.id)
            )
            integration_configs = result.scalars().all()
            
            for integration_config in integration_configs:
                integration_config_copy = IntegrationConfig(
                    integration_id=integration_config.integration_id,  # This would need mapping if integrations were copied
                    user_id=integration_config.user_id,
                    config=integration_config.config.copy() if integration_config.config else None,
                    credentials=integration_config.credentials.copy() if integration_config.credentials else None,
                    is_active=integration_config.is_active,
                    agent_id=agent_copy.id
                )
                self.db.add(integration_config_copy)
            
            await self.db.flush()
            logger.debug(f"Copied {len(integrations)} integrations and {len(integration_configs)} integration configs")
            
        except Exception as e:
            logger.error(f"Failed to copy integrations: {str(e)}", exc_info=True)
            raise
    
    async def _copy_hooks(self, original_agent: AgentModel, agent_copy: AgentModel) -> None:
        """Copy agent hooks"""
        try:
            logger.debug(f"Copying hooks for agent {original_agent.id}")
            
            result = await self.db.execute(
                select(Hook).where(Hook.agent_id == original_agent.id)
            )
            hooks = result.scalars().all()
            
            for hook in hooks:
                hook_copy = Hook(
                    name=hook.name,
                    description=hook.description,
                    hook_type=hook.hook_type,
                    trigger=hook.trigger,
                    trigger_conditions=hook.trigger_conditions.copy() if hook.trigger_conditions else None,
                    action_config=hook.action_config.copy() if hook.action_config else None,
                    priority=hook.priority,
                    is_global=hook.is_global,
                    dependencies=hook.dependencies.copy() if hook.dependencies else None,
                    timeout=hook.timeout,
                    status=hook.status,
                    agent_id=agent_copy.id
                )
                self.db.add(hook_copy)
            
            await self.db.flush()
            logger.debug(f"Copied {len(hooks)} hooks")
            
        except Exception as e:
            logger.error(f"Failed to copy hooks: {str(e)}", exc_info=True)
            raise
    
    async def _copy_communication_channels(self, original_agent: AgentModel, agent_copy: AgentModel) -> None:
        """Copy communication channels"""
        try:
            logger.debug(f"Copying communication channels for agent {original_agent.id}")
            
            result = await self.db.execute(
                select(CommunicationChannel).where(CommunicationChannel.agent_id == original_agent.id)
            )
            channels = result.scalars().all()
            
            for channel in channels:
                channel_copy = CommunicationChannel(
                    name=channel.name,
                    channel_type=channel.channel_type,
                    is_active=channel.is_active,
                    config=channel.config.copy() if channel.config else None,
                    webhook_url=channel.webhook_url,
                    bot_token=channel.bot_token,
                    api_key=channel.api_key
                )
                self.db.add(channel_copy)
            
            await self.db.flush()
            logger.debug(f"Copied {len(channels)} communication channels")
            
        except Exception as e:
            logger.error(f"Failed to copy communication channels: {str(e)}", exc_info=True)
            raise
    
    async def _copy_agent_tables(self, original_agent: AgentModel, agent_copy: AgentModel) -> None:
        """Copy agent tables"""
        try:
            logger.debug(f"Copying agent tables for agent {original_agent.id}")
            
            result = await self.db.execute(
                select(AgentTable).where(AgentTable.agent_id == original_agent.id)
            )
            tables = result.scalars().all()
            
            for table in tables:
                table_copy = AgentTable(
                    name=table.name,
                    display_name=table.display_name,
                    description=table.description,
                    schema=table.schema.copy() if table.schema else None,
                    is_active=table.is_active,
                    max_records=table.max_records,
                    agent_id=agent_copy.id,
                    user_id=agent_copy.owner_id
                )
                self.db.add(table_copy)
            
            await self.db.flush()
            logger.debug(f"Copied {len(tables)} agent tables")
            
        except Exception as e:
            logger.error(f"Failed to copy agent tables: {str(e)}", exc_info=True)
            raise
    
    async def _copy_agent_memories(self, original_agent: AgentModel, agent_copy: AgentModel) -> None:
        """Copy agent memories"""
        try:
            logger.debug(f"Copying agent memories for agent {original_agent.id}")
            
            result = await self.db.execute(
                select(AgentMemory).where(AgentMemory.agent_id == original_agent.id)
            )
            memories = result.scalars().all()
            
            for memory in memories:
                memory_copy = AgentMemory(
                    memory_type=memory.memory_type,
                    importance=memory.importance,
                    content=memory.content,
                    summary=memory.summary,
                    context=memory.context.copy() if memory.context else None,
                    tags=memory.tags.copy() if memory.tags else None,
                    embedding=memory.embedding.copy() if memory.embedding else None,
                    relevance_score=memory.relevance_score,
                    access_count=memory.access_count,
                    last_accessed_at=memory.last_accessed_at,
                    expires_at=memory.expires_at,
                    is_active=memory.is_active,
                    agent_id=agent_copy.id,
                    user_id=agent_copy.owner_id
                )
                self.db.add(memory_copy)
            
            await self.db.flush()
            logger.debug(f"Copied {len(memories)} agent memories")
            
        except Exception as e:
            logger.error(f"Failed to copy agent memories: {str(e)}", exc_info=True)
            raise
    
    async def _copy_voice_configuration(self, original_agent: AgentModel, agent_copy: AgentModel) -> None:
        """Copy voice configuration"""
        try:
            logger.debug(f"Copying voice configuration for agent {original_agent.id}")
            
            if original_agent.voice_configuration:
                voice_config = original_agent.voice_configuration
                voice_config_copy = VoiceConfiguration(
                    voice_enabled=voice_config.voice_enabled,
                    stt_provider=voice_config.stt_provider,
                    stt_model=voice_config.stt_model,
                    stt_language=voice_config.stt_language,
                    stt_config=voice_config.stt_config.copy() if voice_config.stt_config else None,
                    tts_provider=voice_config.tts_provider,
                    tts_model=voice_config.tts_model,
                    tts_voice=voice_config.tts_voice,
                    tts_voice_gender=voice_config.tts_voice_gender,
                    tts_speed=voice_config.tts_speed,
                    tts_pitch=voice_config.tts_pitch,
                    tts_config=voice_config.tts_config.copy() if voice_config.tts_config else None,
                    audio_format=voice_config.audio_format,
                    sample_rate=voice_config.sample_rate,
                    bit_rate=voice_config.bit_rate,
                    noise_reduction=voice_config.noise_reduction,
                    echo_cancellation=voice_config.echo_cancellation,
                    auto_gain_control=voice_config.auto_gain_control,
                    voice_activity_detection=voice_config.voice_activity_detection,
                    allow_interruption=voice_config.allow_interruption,
                    interruption_threshold=voice_config.interruption_threshold,
                    agent_id=agent_copy.id,
                    user_id=agent_copy.owner_id
                )
                self.db.add(voice_config_copy)
            
            await self.db.flush()
            logger.debug("Copied voice configuration")
            
        except Exception as e:
            logger.error(f"Failed to copy voice configuration: {str(e)}", exc_info=True)
            raise
    
    def _prepare_copy_metadata(self, original_metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare metadata for the copied agent"""
        metadata = original_metadata.copy() if original_metadata else {}
        
        # Add copy information
        metadata["marketplace_copy"] = {
            "is_copy": True,
            "original_agent_id": None,  # Will be set in _add_marketplace_metadata
            "copy_timestamp": datetime.utcnow().isoformat(),
            "listing_id": None  # Will be set in _add_marketplace_metadata
        }
        
        return metadata
    
    async def _add_marketplace_metadata(
        self,
        agent_copy: AgentModel,
        listing: MarketplaceListing,
        original_agent: AgentModel
    ) -> None:
        """Add marketplace metadata to the copied agent"""
        try:
            logger.debug(f"Adding marketplace metadata to agent copy {agent_copy.id}")
            
            if not agent_copy.metadata:
                agent_copy.metadata = {}
            
            agent_copy.metadata["marketplace_copy"] = {
                "is_copy": True,
                "original_agent_id": original_agent.id,
                "original_agent_name": original_agent.name,
                "listing_id": listing.id,
                "listing_title": listing.title,
                "author_id": listing.author_id,
                "copy_timestamp": datetime.utcnow().isoformat(),
                "source_version": original_agent.version
            }
            
            # Add tags to indicate this is a marketplace copy
            if not agent_copy.tags:
                agent_copy.tags = []
            
            if "marketplace-copy" not in agent_copy.tags:
                agent_copy.tags.append("marketplace-copy")
            
            if f"copy-of-{original_agent.id}" not in agent_copy.tags:
                agent_copy.tags.append(f"copy-of-{original_agent.id}")
            
            logger.debug(f"Added marketplace metadata to agent {agent_copy.id}")
            
        except Exception as e:
            logger.error(f"Failed to add marketplace metadata: {str(e)}", exc_info=True)
            raise
    
    async def get_copied_agents_for_user(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> List[AgentModel]:
        """Get all agents copied by a user from marketplace"""
        try:
            logger.debug(f"Fetching copied agents for user {user_id}")
            
            # Query agents that have marketplace copy metadata
            result = await self.db.execute(
                select(AgentModel).where(
                    and_(
                        AgentModel.owner_id == user_id,
                        AgentModel.metadata["marketplace_copy"]["is_copy"].astext == "true"
                    )
                ).order_by(AgentModel.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            
            agents = result.scalars().all()
            logger.debug(f"Found {len(agents)} copied agents for user {user_id}")
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to get copied agents for user {user_id}: {str(e)}", exc_info=True)
            return []
    
    async def get_copy_statistics_for_listing(
        self,
        listing_id: int
    ) -> Dict[str, Any]:
        """Get statistics about how many times a listing has been copied"""
        try:
            logger.debug(f"Fetching copy statistics for listing {listing_id}")
            
            # Get installation count from marketplace listing
            result = await self.db.execute(
                select(MarketplaceListing.install_count).where(MarketplaceListing.id == listing_id)
            )
            install_count = result.scalar_one_or_none()
            
            # Get additional statistics
            result = await self.db.execute(
                select(MarketplaceInstallation).where(MarketplaceInstallation.listing_id == listing_id)
            )
            installations = result.scalars().all()
            
            # Calculate recent installs (last 7 days)
            one_week_ago = datetime.utcnow().replace(day=datetime.utcnow().day - 7)
            recent_installs = len([i for i in installations if i.installed_at > one_week_ago])
            
            stats = {
                "total_installs": install_count or 0,
                "recent_installs": recent_installs,
                "unique_users": len(set(i.user_id for i in installations))
            }
            
            logger.debug(f"Copy statistics for listing {listing_id}: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get copy statistics for listing {listing_id}: {str(e)}", exc_info=True)
            return {
                "total_installs": 0,
                "recent_installs": 0,
                "unique_users": 0
            }


# Dependency injection
async def get_marketplace_engine(db: AsyncSession = Depends(get_db)):
    """Get marketplace engine instance"""
    return MarketplaceEngine(db)