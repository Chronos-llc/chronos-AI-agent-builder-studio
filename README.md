# Chronos AI Agent Builder Studio

A comprehensive platform for building, managing, and deploying AI agents with advanced configuration capabilities.

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

1. Start the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
