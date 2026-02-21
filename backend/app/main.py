from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, agents, usage, templates, websocket, actions, integrations, mcp, enhanced_mcp, ai_providers, integration_monitoring, communication_channels, webchat, knowledge, training, meta_agent, personal_access_tokens, messaging_api, marketplace, admin_auth, fuzzy_tools, voice, virtual_computer, workflow_generation, user_profiles, conversations, agentic_thinking, phone_numbers, integration_moderation, integration_admin_management, support_system, payment_methods, platform_updates, skills, skills_marketplace
from app.core.logging import setup_logging
from app.core.mcp_client import initialize_mcp_integrations
from app.core.enhanced_mcp_manager import initialize_enhanced_mcp
from app.core.ai_providers import initialize_ai_providers
from app.core.integration_monitoring import initialize_integration_monitoring
from app.core.communication_channels import initialize_communication_channels
from app.core.webchat import initialize_webchat
from app.core.object_storage import initialize_object_storage
from app.core.agent_engine import initialize_agent_engine, cleanup_agent_engine
from app.core.data_retention import purge_due_deleted_users, retention_loop
from app.core.skills_schema_alignment import ensure_skills_schema_alignment
from scripts.initialize_mcp_integrations import initialize_mcp_integrations
from scripts.seed_skills_marketplace import seed_skills_marketplace

# Setup logging
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Chronos AI Agent Builder Studio")
    retention_task: asyncio.Task | None = None
      
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Align legacy skills tables with current model columns.
    await ensure_skills_schema_alignment()

    # Seed default marketplace skills (idempotent).
    await seed_skills_marketplace()

    # Prepare object storage bucket (non-fatal in dev if unavailable).
    await initialize_object_storage()
      
    # Initialize AgentEngine for training
    await initialize_agent_engine()
      
    # Initialize MCP integrations
    await initialize_enhanced_mcp()
      
    # Initialize MCP server integrations for the Hub Marketplace
    await initialize_mcp_integrations()
      
    # Initialize AI providers
    await initialize_ai_providers()
      
    # Initialize integration monitoring
    await initialize_integration_monitoring()
      
    # Initialize communication channels
    await initialize_communication_channels()
      
    # Initialize WebChat
    await initialize_webchat()

    # Run retention purge on startup and then continue in background
    await purge_due_deleted_users()
    retention_task = asyncio.create_task(retention_loop())
     
    yield
     
    # Shutdown
    logger.info("Shutting down Chronos AI Agent Builder Studio")

    if retention_task:
        retention_task.cancel()
        try:
            await retention_task
        except asyncio.CancelledError:
            pass
     
    # Cleanup AgentEngine
    await cleanup_agent_engine()


# Create FastAPI application
app = FastAPI(
    title="Chronos AI Agent Builder Studio API",
    description="A comprehensive platform for building, managing, and deploying AI agents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|192\.168\.\d+\.\d+)(:\d+)?$"
    if settings.ENVIRONMENT == "development"
    else None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(user_profiles.router, prefix="/api/v1", tags=["user-profiles"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(actions.router, prefix="/api/v1", tags=["actions", "hooks"])
app.include_router(usage.router, prefix="/api/v1/usage", tags=["usage"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(integration_moderation.router, prefix="/api/v1", tags=["integration-moderation"])
app.include_router(integration_admin_management.router, prefix="/api/v1", tags=["integration-admin-management"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])  # Original MCP endpoints
app.include_router(enhanced_mcp.router, prefix="/api/v1", tags=["enhanced-mcp"])  # Enhanced MCP endpoints
app.include_router(ai_providers.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(voice.router, prefix="/api/v1", tags=["voice"])
app.include_router(phone_numbers.router, prefix="/api/v1", tags=["phone-numbers"])
app.include_router(virtual_computer.router, prefix="/api/v1", tags=["virtual-computer"])
app.include_router(integration_monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(communication_channels.router, prefix="/api/v1/communication", tags=["communication"])
app.include_router(webchat.router, prefix="/api/v1/webchat", tags=["webchat"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(training.router, prefix="/api/v1", tags=["training"])
app.include_router(workflow_generation.router, prefix="/api/v1/workflow-generation", tags=["workflow-generation"])
app.include_router(conversations.router, prefix="/api/v1", tags=["conversations"])
app.include_router(agentic_thinking.router, prefix="/api/v1", tags=["agentic-thinking"])
app.include_router(meta_agent.router, prefix="/api/v1/meta-agent", tags=["meta-agent"])
app.include_router(personal_access_tokens.router, prefix="/api/v1/personal-access-tokens", tags=["personal-access-tokens"])
app.include_router(messaging_api.router, prefix="/api/v1/messaging", tags=["messaging-api"])
app.include_router(marketplace.router, prefix="/api/v1/marketplace", tags=["marketplace"])
app.include_router(admin_auth.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(fuzzy_tools.router, tags=["fuzzy-tools"])  # FUZZY studio manipulation tools
app.include_router(support_system.router, prefix="/api/support", tags=["support-system"])
app.include_router(payment_methods.router, prefix="/api/payment", tags=["payment-methods"])
app.include_router(platform_updates.router, prefix="/api", tags=["platform-updates"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(skills_marketplace.router, prefix="/api/skills", tags=["skills-marketplace"])


@app.get("/")
async def root():
    return {
        "message": "Chronos AI Agent Builder Studio API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chronos-backend"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development"
    )
