from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, agents, usage, templates, websocket, actions, integrations, mcp, ai_providers, integration_monitoring, communication_channels, webchat, knowledge
from app.core.logging import setup_logging
from app.core.mcp_client import initialize_mcp_integrations
from app.core.ai_providers import initialize_ai_providers
from app.core.integration_monitoring import initialize_integration_monitoring
from app.core.communication_channels import initialize_communication_channels
from app.core.webchat import initialize_webchat

# Setup logging
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Chronos AI Agent Builder Studio")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize MCP integrations
    await initialize_mcp_integrations()
    
    # Initialize AI providers
    await initialize_ai_providers()
    
    # Initialize integration monitoring
    await initialize_integration_monitoring()
    
    # Initialize communication channels
    await initialize_communication_channels()
    
    # Initialize WebChat
    await initialize_webchat()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Chronos AI Agent Builder Studio")


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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(actions.router, prefix="/api/v1", tags=["actions", "hooks"])
app.include_router(usage.router, prefix="/api/v1/usage", tags=["usage"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])
app.include_router(ai_providers.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(integration_monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(communication_channels.router, prefix="/api/v1/communication", tags=["communication"])
app.include_router(webchat.router, prefix="/api/v1/webchat", tags=["webchat"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])


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