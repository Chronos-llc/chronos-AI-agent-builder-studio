# 🚀 Chronos AI Agent Builder Studio - Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Node.js (v18 or higher)
- Python (v3.9 or higher)
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

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
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
- **AI provider integrations** (OpenAI, Anthropic)
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
