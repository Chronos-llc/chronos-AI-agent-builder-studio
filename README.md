# Chronos AI Agent Builder Studio

A comprehensive platform for building, managing, and deploying AI agents with advanced configuration capabilities.

## Documentation

A professional documentation site is available at `docs-site/` directory, built with Docusaurus.

### Features

- **User Guide**: Detailed instructions for using the Chronos AI platform
- **API Guide**: Comprehensive API documentation
- **Agentic Thinking**: Documentation for the experimental planning mode
- **Playwright Deployment**: Guide for deploying Playwright MCP server
- **Search Functionality**: Full-text search across all documentation
- **Dark Theme**: Modern dark theme with cyan accents matching Chronos brand

### Running the Documentation Site

```bash
# Navigate to documentation site directory
cd docs-site

# Install dependencies (first time only)
npm install

# Start development server (runs on http://localhost:3000)
npm start

# Build for production
npm run build

# Serve production build locally
npm run serve
```

### Documentation Site Structure

```
docs-site/
├── docs/                    # Documentation content
│   ├── user-guide.md       # User Guide
│   ├── api-guide.md        # API Guide
│   ├── agentic-thinking.md # Agentic Thinking feature
│   └── playwright-deployment.md # Playwright deployment guide
├── src/                     # Docusaurus theme and customizations
├── docusaurus.config.ts    # Site configuration
├── sidebars.ts             # Documentation sidebar configuration
└── package.json            # Dependencies and scripts
```

## Features

- 🤖 **Agent Builder**: Visual interface for creating and configuring AI agents
- 🔧 **Version Control**: Track agent iterations and deployments
- 🔗 **Integrations**: Connect with external services, APIs, and MCP servers
- 📊 **Analytics**: Monitor agent performance and usage
- 🔒 **Authentication**: Secure JWT-based authentication system
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Architecture

This project uses a modern monorepo architecture with:

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Cache**: Redis for sessions and caching
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT tokens with refresh mechanism

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10-3.12 (64-bit recommended for local development; required for prebuilt database driver wheels like `psycopg2-binary`)

### MCP Server Integrations

The Chronos Hub Marketplace now includes two powerful MCP server integrations:

1. **Playwright MCP Server** - Web automation and testing with vision capabilities
2. **Memory MCP Server** - Persistent memory and conversation history

These integrations are automatically initialized when you start the backend.

### AI Provider Integrations

Seed the AI providers into the Integrations hub:

```bash
python backend/scripts/seed_ai_provider_integrations.py
```

Then add your default API keys to `.env` (for example `OPENAI_API_KEY`, `FIREWORKS_API_KEY`, `XAI_API_KEY`, `OPENROUTER_API_KEY`, and any STT/TTS keys). Install providers from the Integrations page to make their models available in the Studio model pickers.

### Using Docker (Recommended)

1. Clone the repository:

```bash
git clone <repository-url>
cd chronos-ai-agent-builder-studio
```

1. Copy environment variables:

```bash
cp .env.example .env
```

1. Start the development environment:

```bash
docker-compose up --build
```

1. Access the application:
   - Frontend: <http://localhost:3000>
   - Backend API: <http://localhost:8000>
   - API Documentation: <http://localhost:8000/docs>
   - Chronos Hub Marketplace: <http://localhost:3000/integrations>

### Local Development

#### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

1. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Set up database:

```bash
alembic upgrade head
```

1. Start the server (from repo root):

```bash
cd ..
python -m uvicorn app.main:app --app-dir backend --reload-dir backend --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

1. Install dependencies:

```bash
npm install
```

1. Start the development server:

```bash
npm run dev
```

> Dev-mode note: Vite serves source modules for fast HMR. In browser DevTools/Network you will see module paths (for example `/src/...`) while running `npm run dev`. This is expected for development and is not a production deployment mode.

## Project Structure

```
chronos-ai-agent-builder/
├── frontend/                 # React + TypeScript app
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API service functions
│   │   ├── store/           # State management
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── backend/                  # FastAPI app
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # Application entry point
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/             # API routes
│   │   ├── core/            # Core configuration
│   │   └── db/              # Database configuration
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml       # Development setup
├── .env.example
└── README.md
```

## API Documentation

Once the backend is running, you can access the interactive API documentation at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Database Schema

The application uses the following main entities:

- **Users**: User accounts and authentication
- **Agents**: AI agent configurations
- **AgentVersions**: Version control for agents
- **Actions**: Available actions for agents
- **Hooks**: Event hooks and triggers
- **Integrations**: External service integrations including MCP servers
- **Settings**: Application and user settings

## Development

### MCP Integrations

To manually initialize MCP integrations:

```bash
cd backend
python scripts/run_initialize_mcp_integrations.py
```

To test MCP integrations:

```bash
cd backend
python test_mcp_integrations.py
```

### Database Migrations

To create a new migration:

```bash
cd backend
alembic revision --autogenerate -m "Description"
```

To apply migrations:

```bash
alembic upgrade head
```

### Testing

Backend tests:

```bash
cd backend
pytest
```

Frontend tests:

```bash
cd frontend
npm run test
```

## Deployment

For production deployment, ensure you:

1. Update environment variables with production values
2. Use a proper secret key for JWT tokens
3. Configure proper CORS origins
4. Set up SSL certificates
5. Use a production-ready database setup

### Deferred Frontend Hardening Checklist (for production pass)

The current workspace is intentionally running frontend in development mode. When you switch to production rollout, apply this checklist:

1. Build and serve static assets only (`npm run build` + static server such as Nginx)
2. Disable source maps in production builds
3. Block access to `*.map` and `/src/*` paths at the web server
4. Add strict security headers (CSP, X-Content-Type-Options, Referrer-Policy, frame protections)
5. Remove any development-only host/port and hot-reload settings from deployment manifests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
