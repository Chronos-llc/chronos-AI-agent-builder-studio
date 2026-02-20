# 🚀 Chronos AI Agent Builder Studio - Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Node.js (v18 or higher)
- Python 3.10-3.12 (64-bit recommended)
- pip (Python package manager)

## Step-by-Step Startup Instructions

### 1. Start Database Services

Open a terminal in the project root and run:

```bash
docker-compose up -d postgres redis
```

This will start:

- PostgreSQL database on localhost:5432
- Redis cache on localhost:6379

### 1b. Start Object Storage (MinIO)

Skills, knowledge uploads, screenshots, and marketplace media now use object storage.

```bash
docker-compose up -d minio minio-init
```

This will start:

- MinIO API on localhost:9000
- MinIO Console on localhost:9001
- Bucket bootstrap via `minio-init` (`chronos-objects`)

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2b. Seed AI Provider Integrations (Recommended)

```bash
python backend/scripts/seed_ai_provider_integrations.py
```

### 3. Start Backend Server

```bash
cd ..
python -m uvicorn app.main:app --app-dir backend --reload-dir backend --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at:

- **API**: <http://localhost:8000>
- **API Documentation**: <http://localhost:8000/docs>

### 4. Install Frontend Dependencies

Open a new terminal:

```bash
cd frontend
npm install
```

### 5. Start Frontend Server

```bash
cd frontend
npm run dev
```

The frontend will be available at:

- **Frontend**: <http://localhost:3000>

## Object Storage Backfill (existing local records)

After enabling object storage, migrate legacy file/image rows:

```bash
cd backend
python scripts/backfill_object_storage_objects.py
```

Report output is written to:

- `backend/backfill_object_storage_report.json`

## 🎉 Access Your Application

Once both servers are running, you can access:

1. **Main Application**: <http://localhost:3000>
2. **API Documentation**: <http://localhost:8000/docs>
3. **Health Check**: <http://localhost:8000/health>

## 🧪 Test the Application

1. **Register a new user** at <http://localhost:3000/login>
2. **Create your first agent** using the Studio interface
3. **Upload knowledge files** to test the knowledge base
4. **Test real-time collaboration** features
5. **Explore API endpoints** in the documentation

### Skills Marketplace E2E Smoke (upload -> review -> publish -> install)

```bash
cd frontend
npm run e2e
```

This runs Playwright against:

- frontend: `http://127.0.0.1:3000`
- backend: `http://127.0.0.1:8000`
- MinIO: `http://127.0.0.1:9000`

## 📁 Project Structure

```
chronos-ai-agent-builder-studio/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core utilities
│   │   ├── models/         # Database models
│   │   └── schemas/        # Pydantic schemas
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts
│   │   ├── pages/          # Page components
│   │   └── hooks/          # Custom hooks
│   └── package.json        # Node dependencies
└── docker-compose.yml      # Docker services
```

## 🔧 Development Features

- **Real-time collaboration** via WebSocket
- **File upload** and knowledge base management
- **AI provider integrations** (OpenAI, Fireworks AI, xAI, OpenRouter, and voice/STT/TTS providers)
- **JWT authentication** with refresh tokens
- **Comprehensive API** with documentation
- **Testing framework** with pytest

## 🛠️ Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Ensure Docker is running
2. Check that PostgreSQL container started: `docker ps`
3. Verify database credentials in `.env` file

### Port Conflicts

If ports are already in use:

- Backend: Change API_PORT in `.env` to 8001
- Frontend: Update the port in `frontend/vite.config.ts`
- Database: Modify ports in `docker-compose.yml`

### Windows Build Tooling / Python Version Issues

If you see wheel build errors for `pydantic-core`, `greenlet`, or `httptools` on Windows:

1. Install **Python 3.10-3.12 (64-bit)** and re-run `pip install -r backend/requirements.txt`.
2. Ensure **Microsoft C++ Build Tools** are installed (select the "C++ build tools" workload).
3. Install **Rust** (via <https://rustup.rs/>) if you still need to build native wheels.

These packages do not currently ship wheels for Python 3.14 32-bit, so that combination will fail to build from source.

If you see `pg_config executable not found` while installing `psycopg2` or `psycopg2-binary`:

1. Confirm you're installing **`psycopg2-binary`**, not `psycopg2` (the backend uses `psycopg2-binary` in `backend/requirements.txt`).
2. Make sure you're using **Python 3.10-3.12 (64-bit)** so pip can download prebuilt wheels.
3. If you must build from source, install **PostgreSQL** and add its `bin` directory (which contains `pg_config`) to your `PATH`.
4. Re-run `pip install -r backend/requirements.txt`.
### Frontend Build Issues

If frontend fails to build:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## 📞 Need Help?

The application includes:

- ✅ Complete API documentation at `/docs`
- ✅ Health check endpoint at `/health`
- ✅ Error logging and debugging information
- ✅ Test suite for validation

Happy building! 🎉
